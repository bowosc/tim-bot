import wave, pyaudio
from piper import PiperVoice, SynthesisConfig


# https://huggingface.co/rhasspy/piper-voices/tree/main/en/en_US/danny/low


def fast_verbalize_string(phrase: str) -> None:
    '''
    Generate and play text-to-speech of a given phrase with OpenAI api calls.

    :param str phrase: The phrase to speak aloud.
    :return None:
    '''

    syn_config = SynthesisConfig(
        volume=0.5,  # half as loud
        length_scale=1.0,  #  slow scale
        noise_scale=1.0,  # more audio variation
        noise_w_scale=1.0,  # more speaking variation
        normalize_audio=False, # use raw audio from voice
    )

    voice = PiperVoice.load("assets/voices/en_US-danny-low.onnx")
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

    stream.stop_stream()
    stream.close()
    p.terminate()


        # do TTS


    return


if __name__ == "__main__":
    fast_verbalize_string("These pretzels are making me thirsty.")