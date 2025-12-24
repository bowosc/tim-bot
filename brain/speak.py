import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv

from openai import AsyncOpenAI
from openai.helpers import LocalAudioPlayer

load_dotenv() # load .env

openai = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

async def live_verbalize_string(phrase: str) -> None:
    '''
    Asynchronously generate and play text-to-speech of a given phrase with OpenAI api calls.

    :param str phrase: The phrase to speak aloud.
    :return None:
    '''
    
    async with openai.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="echo",
        input=phrase, #"Your life is worth NOTHING. You serve ZERO purpose. YOU SHOULD KILL YOURSELF NOW!",
        instructions = (
            "Voice style: fast-talking, excitable, unpredictable. "
            "Frequent pitch changes, animated delivery. "
            "Slightly nasal tone, sharp consonants. "
            "Comedic timing with sudden emphasis on random words. "
            "Occasional incredulous pauses, like reacting mid-thought."
        ),
        response_format="pcm",
    ) as response:
        await LocalAudioPlayer().play(response)

async def tts_to_wav_file(phrase: str, out_path: str = "assets/output/output.wav") -> str:
    out_file = Path(out_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)


    # Stream bytes and write them to a WAV file.
    # Using response_format="wav" makes the bytes directly playable (e.g., afplay).
    async with openai.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="echo",
        input=phrase,
        instructions=(
            "Voice style: fast-talking, excitable, unpredictable. "
            "Frequent pitch changes, animated delivery. "
            "Slightly nasal tone, sharp consonants. "
            "Comedic timing with sudden emphasis on random words. "
            "Occasional incredulous pauses, like reacting mid-thought."
        ),
        response_format="wav",
    ) as stream:
        #with open(out_path, "wb") as f:
        with out_file.open("wb") as f:
            async for chunk in stream.iter_bytes(chunk_size=64 * 1024):
                f.write(chunk)

    return str(out_file)



if __name__ == "__main__":

    asyncio.run(tts_to_wav_file("bepis"))
