import os, asyncio, pyaudio, wave, threading, time


import pyaudio, wave, threading
import pyaudio, wave, threading, audioop

def record_audio(filename, chunk=2048, device_index=1, out_rate=48000):
    p = pyaudio.PyAudio()
    dev = p.get_device_info_by_index(device_index)
    in_rate = int(dev["defaultSampleRate"])  # BoPodsPro is 24000

    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=in_rate,
        input=True,
        input_device_index=device_index,
        frames_per_buffer=chunk,
    )

    print("Press Enter to start recording...")
    input()
    print("Recording started. Press Enter again to stop...")

    frames = []
    recording = True

    def stop_on_enter():
        nonlocal recording
        input()
        recording = False
        print("Recording stopped.")

    threading.Thread(target=stop_on_enter, daemon=True).start()

    while recording:
        frames.append(stream.read(chunk, exception_on_overflow=False))

    stream.stop_stream()
    stream.close()
    p.terminate()

    raw = b"".join(frames)

    # Save at out_rate for broad compatibility (or set out_rate=in_rate to skip resample)
    if out_rate != in_rate:
        raw, _ = audioop.ratecv(raw, 2, 1, in_rate, out_rate, None)
        save_rate = out_rate
    else:
        save_rate = in_rate

    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(save_rate)
        wf.writeframes(raw)

    print(f"Saved {filename} (recorded {in_rate} Hz, saved {save_rate} Hz)")





if __name__ == "__main__":
    record_audio("test.wav")