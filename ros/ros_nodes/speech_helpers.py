import os

import pyaudio
from piper import PiperVoice, SynthesisConfig


VOICE_MODEL_PATH = os.getenv(
    "TIM_BOT_PIPER_MODEL",
    "assets/voices/en_US-danny-low.onnx",
)


def fast_verbalize_string(phrase: str) -> None:
    syn_config = SynthesisConfig(
        volume=0.5,
        length_scale=1.0,
        noise_scale=1.0,
        noise_w_scale=1.0,
        normalize_audio=False,
    )

    voice = PiperVoice.load(VOICE_MODEL_PATH)
    p = pyaudio.PyAudio()
    stream = None

    for chunk in voice.synthesize(phrase, syn_config):
        if stream is None:
            stream = p.open(
                format=p.get_format_from_width(chunk.sample_width),
                channels=chunk.sample_channels,
                rate=chunk.sample_rate,
                output=True,
            )
        stream.write(chunk.audio_int16_bytes)

    if stream is not None:
        stream.stop_stream()
        stream.close()
    p.terminate()
