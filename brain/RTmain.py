import os, json, base64
from dotenv import load_dotenv
import websocket

from tools import flicker_led, check_camera

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

MODEL = "gpt-realtime"  # pick the realtime model you’re using
URL = f"wss://api.openai.com/v1/realtime?model={MODEL}"

# register tools you want the model to be able to call
TOOL_REGISTRY = {
    "flicker_led": flicker_led,
    "check_camera": check_camera,
}

TOOLS_SCHEMA = [
    {
        "type": "function",
        "name": "flicker_led",
        "description": "Flicker the robot LED.",
        "parameters": {                             # hallucinated
            "type": "object",
            "properties": {
                "count": {"type": "integer", "description": "How many flickers."}
            },
            "required": ["count"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "check_camera",
        "description": "Check the camera and describe what it sees.",
        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    },
]

def ws_send(ws, event: dict):
    ws.send(json.dumps(event))

def send_session_update(ws):
    ws_send(ws, {
        "type": "session.update",
        "session": {
            "instructions": "You are a robot that has an LED light and a camera.",
            "modalities": ["text", "audio"],  # you can do speech out if you want
            "tools": TOOLS_SCHEMA,
            "tool_choice": "auto",
        }
    })
    # server replies with session.updated :contentReference[oaicite:1]{index=1}

def send_user_text(ws, text: str):
    ws_send(ws, {
        "type": "conversation.item.create",
        "item": {
            "type": "message",
            "role": "user",
            "content": [{"type": "input_text", "text": text}],
        }
    })
    # Start the model response after adding input :contentReference[oaicite:2]{index=2}
    ws_send(ws, {"type": "response.create"})

def send_user_image(ws, jpeg_bytes: bytes, prompt_text: str = ""):
    ws_send(ws, {
        "type": "conversation.item.create",
        "item": {
            "type": "message",
            "role": "user",
            "content": [
                *([{"type": "input_text", "text": prompt_text}] if prompt_text else []),
                {"type": "input_image", "image_base64": base64.b64encode(jpeg_bytes).decode("utf-8")},
            ]
        }
    })
    ws_send(ws, {"type": "response.create"})  # kick off response :contentReference[oaicite:3]{index=3}

def run():
    ws = websocket.create_connection(
        URL,
        header=[
            f"Authorization: Bearer {API_KEY}",
        ],
    )

    # Track streamed function-call args by call_id
    call_args_buf = {}  # call_id -> string buffer

    while True:
        event = json.loads(ws.recv())
        etype = event.get("type")

        if etype == "session.created":
            send_session_update(ws)

        elif etype == "response.output_text.delta":
            print(event.get("delta", ""), end="", flush=True)

        # 2) Function call args can stream in pieces; accumulate them
        elif etype == "response.function_call_arguments.delta":
            call_id = event["call_id"]
            call_args_buf[call_id] = call_args_buf.get(call_id, "") + event.get("delta", "")

        # 3) When done, execute tool + send function_call_output back
        elif etype == "response.function_call_arguments.done":
            call_id = event["call_id"]
            fn_name = event["name"]
            args_json = call_args_buf.pop(call_id, "") or "{}"

            try:
                args = json.loads(args_json)
            except json.JSONDecodeError:
                args = {}

            fn = TOOL_REGISTRY.get(fn_name)
            if fn is None:
                tool_output = {"ok": False, "error": f"Unknown tool: {fn_name}"}
            else:
                try:
                    result = fn(**args)  # run your tool
                    tool_output = {"ok": True, "result": result}
                except Exception as e:
                    tool_output = {"ok": False, "error": str(e)}

            ws_send(ws, {
                "type": "conversation.item.create",
                "item": {
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": json.dumps(tool_output),
                }
            })  # tool output item :contentReference[oaicite:4]{index=4}

            # Then let the model continue after tool output
            ws_send(ws, {"type": "response.create"})

        elif etype == "response.done":
            print("\n---\n")

if __name__ == "__main__":
    run()
