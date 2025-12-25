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

default_voice_instr = (
    "Voice style: fast-talking, excitable, unpredictable. "
    "Frequent pitch changes, animated delivery. "
    "Slightly nasal tone, sharp consonants. Deep voice."
    "Comedic timing with sudden emphasis on random words. "
    "Occasional incredulous pauses, like reacting mid-thought."
)

async def live_verbalize_string(phrase: str, instructions: str = "") -> None:
    '''
    Asynchronously generate and play text-to-speech of a given phrase with OpenAI api calls.

    :param str phrase: The phrase to speak aloud.
    :return None:
    '''

    instructions = default_voice_instr + f"Just this time: {instructions}"
    
    async with openai.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="echo",
        input=phrase, #"Your life is worth NOTHING. You serve ZERO purpose. YOU SHOULD KILL YOURSELF NOW!",
        instructions = instructions,
        response_format="pcm",
    ) as response:
        await LocalAudioPlayer().play(response)

async def tts_to_wav_file(phrase: str, instructions: str = "", out_path: str = "output/output3.wav") -> str:
    out_file = Path(out_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    instructions = default_voice_instr + f" {instructions}"

    # Stream bytes and write them to a WAV file.
    # Using response_format="wav" makes the bytes directly playable (e.g., afplay).
    async with openai.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="echo",
        input=phrase,
        instructions=instructions,
        response_format="wav",
    ) as stream:
        #with open(out_path, "wb") as f:
        with out_file.open("wb") as f:
            async for chunk in stream.iter_bytes(chunk_size=64 * 1024):
                f.write(chunk)

    return str(out_file)



if __name__ == "__main__":

    asyncio.run(tts_to_wav_file("this is a TEST PHRASE. Hello world."))
