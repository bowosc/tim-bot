import asyncio
import audioop
import threading
import time
import wave

import numpy as np
import pyaudio
import sounddevice as sd
import whisper

SAMPLE_RATE = 16000


def write_wav_file(path: str, sample_rate: int, audio: np.ndarray) -> None:
    audio = np.asarray(audio, dtype=np.float32)
    audio = np.clip(audio, -1.0, 1.0)
    pcm16 = (audio * np.iinfo(np.int16).max).astype(np.int16)

    with wave.open(path, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm16.tobytes())

def record_until_pause(silence_threshold=0.01, silence_duration=0.9, max_recording_seconds=15):
    """
    Records from microphone until speech naturally ends.

    silence_threshold:
        Lower = more sensitive.
        Higher = requires louder speech.

    silence_duration:
        How many seconds of silence means "the sentence ended".
    """

    print("Listening...")

    audio_chunks = []
    started_speaking = False
    silence_start = None
    start_time = time.time()

    chunk_duration = 0.1
    chunk_size = int(SAMPLE_RATE * chunk_duration)

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
        blocksize=chunk_size,
    ) as stream:
        while True:
            chunk, _ = stream.read(chunk_size)
            chunk = chunk.flatten()

            volume = np.sqrt(np.mean(chunk ** 2))

            if volume > silence_threshold:
                started_speaking = True
                silence_start = None
                audio_chunks.append(chunk)

            elif started_speaking:
                audio_chunks.append(chunk)

                if silence_start is None:
                    silence_start = time.time()

                if time.time() - silence_start > silence_duration:
                    break

            if time.time() - start_time > max_recording_seconds:
                break

    if not audio_chunks:
        return None

    audio = np.concatenate(audio_chunks)
    return audio


def listen_and_transcribe(model):
    audio = record_until_pause()

    if audio is None:
        return ""

    # Pass the waveform directly to Whisper so local transcription does not
    # depend on an external ffmpeg binary just to re-read our own temp WAV.
    result = model.transcribe(audio)
    return result["text"].strip()



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
    # record_audio("test.wav")
    while True:
        text = listen_and_transcribe()
        print("You said:", text)
