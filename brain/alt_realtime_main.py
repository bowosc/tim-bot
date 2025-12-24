import os, json, base64, asyncio
from dotenv import load_dotenv

import numpy as np
import sounddevice as sd
import cv2
import websockets

from tools import flicker_led  # , check_camera

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

MODEL = "gpt-realtime"  # set to your realtime-capable model
WS_URL = f"wss://api.openai.com/v1/realtime?model={MODEL}"

# ---- audio settings ----
IN_SR = 24000          # what we send to the model (mic)
OUT_SR = 48000         # what your device runs at (BoPodsPro default_samplerate)
CH = 1
BLOCK_MS = 20
IN_BLOCK_SAMPLES = int(IN_SR * BLOCK_MS / 1000)
OUT_BLOCK_SAMPLES = int(OUT_SR * BLOCK_MS / 1000)

# ---- “video” settings ----
FPS = 0.5
FRAME_INTERVAL = 1.0 / FPS
JPEG_QUALITY = 60

TOOLS = {
    "flicker_led": flicker_led,
    # "check_camera": check_camera,
}

TOOLS_SCHEMA = [
    {
        "type": "function",
        "name": "flicker_led",
        "description": "Flicker the robot LED.",
        "parameters": {
            "type": "object",
            "properties": {"count": {"type": "integer"}},
            "required": ["count"],
            "additionalProperties": False,
        },
    },
]

def upsample_24k_to_48k(pcm16_bytes: bytes) -> bytes:
    """Fast 2x upsample (24k->48k) with linear interpolation."""
    x = np.frombuffer(pcm16_bytes, dtype=np.int16)
    n = len(x)
    if n == 0:
        return pcm16_bytes
    if n == 1:
        return np.repeat(x, 2).astype(np.int16).tobytes()

    y = np.empty(n * 2, dtype=np.int16)
    y[0::2] = x
    y[1:-1:2] = ((x[:-1].astype(np.int32) + x[1:].astype(np.int32)) // 2).astype(np.int16)
    y[-1] = x[-1]
    return y.tobytes()

async def ws_send(ws, obj: dict):
    await ws.send(json.dumps(obj))

async def configure_session(ws):
    await ws_send(ws, {
        "type": "session.update",
        "session": {
            "type": "realtime",
            "output_modalities": ["audio", "text"],
            "instructions": "You are a robot with an LED. Use tools when helpful.",
            "tools": TOOLS_SCHEMA,
            "tool_choice": "auto",
            "audio": {
                "input": {
                    "format": {"type": "audio/pcm", "rate": IN_SR},
                    "turn_detection": {"type": "semantic_vad"},
                },
                # Model output is typically 24k PCM; we’ll resample to 48k for playback.
                "output": {"format": {"type": "audio/pcm", "rate": IN_SR}, "voice": "marin"},
            },
        }
    })

async def mic_task(ws):
    """Capture mic (float32) -> PCM16 @ 24k -> input_audio_buffer.append."""
    q: asyncio.Queue[bytes] = asyncio.Queue()

    def callback(indata, frames, time, status):
        pcm = np.clip(indata[:, 0], -1.0, 1.0)
        pcm16 = (pcm * 32767.0).astype(np.int16).tobytes()
        try:
            q.put_nowait(pcm16)
        except asyncio.QueueFull:
            pass

    stream = sd.InputStream(
        samplerate=IN_SR,
        channels=CH,
        dtype="float32",
        blocksize=IN_BLOCK_SAMPLES,
        callback=callback,
    )

    with stream:
        while True:
            chunk = await q.get()
            await ws_send(ws, {
                "type": "input_audio_buffer.append",
                "audio": base64.b64encode(chunk).decode("utf-8")
            })

async def camera_task(ws, device_index=0):
    cap = cv2.VideoCapture(device_index)
    if not cap.isOpened():
        print("Camera not opened; skipping camera_task.")
        return

    try:
        while True:
            ok, frame = cap.read()
            if ok:
                encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY]
                ok2, jpg = cv2.imencode(".jpg", frame, encode_params)
                if ok2:
                    b64 = base64.b64encode(jpg.tobytes()).decode("utf-8")
                    await ws_send(ws, {
                        "type": "conversation.item.create",
                        "item": {
                            "type": "message",
                            "role": "user",
                            "content": [
                                {"type": "input_text", "text": "Latest camera frame."},
                                {"type": "input_image", "image_base64": b64},
                            ],
                        }
                    })
            await asyncio.sleep(FRAME_INTERVAL)
    finally:
        cap.release()

async def speaker_playback_loop():
    """
    Playback sink at 48k. We buffer bytes and feed exactly OUT_BLOCK_SAMPLES each callback.
    """
    play_q: asyncio.Queue[bytes] = asyncio.Queue(maxsize=200)  # ~4s at 20ms blocks
    byte_buf = bytearray()

    def out_cb(outdata, frames, time, status):
        nonlocal byte_buf

        # Pull queued chunks into byte_buf if we’re low
        while len(byte_buf) < frames * 2:  # int16 = 2 bytes
            try:
                byte_buf.extend(play_q.get_nowait())
            except asyncio.QueueEmpty:
                break

        need = frames * 2
        if len(byte_buf) >= need:
            chunk = bytes(byte_buf[:need])
            del byte_buf[:need]
            data = np.frombuffer(chunk, dtype=np.int16)
            outdata[:] = data.reshape(-1, 1)
        else:
            outdata[:] = np.zeros((frames, 1), dtype=np.int16)

    stream = sd.OutputStream(
        samplerate=OUT_SR,
        channels=1,
        dtype="int16",
        blocksize=OUT_BLOCK_SAMPLES,
        callback=out_cb,
    )
    stream.start()
    return play_q, stream

async def event_loop(ws):
    call_arg_buf: dict[str, str] = {}
    play_q, out_stream = await speaker_playback_loop()

    try:
        async for raw in ws:
            ev = json.loads(raw)
            t = ev.get("type")

            if t == "response.output_audio.delta":
                pcm_b64 = ev.get("delta")
                if pcm_b64:
                    pcm24 = base64.b64decode(pcm_b64)          # PCM16 @ 24k
                    pcm48 = upsample_24k_to_48k(pcm24)         # -> PCM16 @ 48k
                    try:
                        play_q.put_nowait(pcm48)
                    except asyncio.QueueFull:
                        # drop if we’re falling behind to keep it “live”
                        pass

            elif t == "response.function_call_arguments.delta":
                call_id = ev["call_id"]
                call_arg_buf[call_id] = call_arg_buf.get(call_id, "") + ev.get("delta", "")

            elif t == "response.function_call_arguments.done":
                call_id = ev["call_id"]
                name = ev["name"]
                args_text = call_arg_buf.pop(call_id, "") or "{}"

                try:
                    args = json.loads(args_text)
                except json.JSONDecodeError:
                    args = {}

                fn = TOOLS.get(name)
                if not fn:
                    result = {"ok": False, "error": f"Unknown tool: {name}"}
                else:
                    try:
                        out = fn(**args)
                        result = {"ok": True, "result": out}
                    except Exception as e:
                        result = {"ok": False, "error": str(e)}

                await ws_send(ws, {
                    "type": "conversation.item.create",
                    "item": {
                        "type": "function_call_output",
                        "call_id": call_id,
                        "output": json.dumps(result),
                    }
                })
                await ws_send(ws, {"type": "response.create"})

    finally:
        out_stream.stop()
        out_stream.close()

async def main():
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}

    async with websockets.connect(WS_URL, extra_headers=headers, max_size=2**24) as ws:
        first = json.loads(await ws.recv())
        if first.get("type") != "session.created":
            print("Unexpected first event:", first)

        await configure_session(ws)

        await ws_send(ws, {
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": "Start. Speak responses out loud, and use tools when needed. Flicker the led immediately."}],
            }
        })
        await ws_send(ws, {"type": "response.create"})

        await asyncio.gather(
            mic_task(ws),
            camera_task(ws, device_index=0),
            event_loop(ws),
        )

if __name__ == "__main__":
    asyncio.run(main())
