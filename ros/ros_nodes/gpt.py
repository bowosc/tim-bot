from openai import OpenAI
from dotenv import load_dotenv
import os
import base64

load_dotenv()
_client = None

DEFAULT_PROMPT = "Give me a short list of objects in this image, seperated by commas. "
JSON_PROMPT = "Generate json data for each object in this image, including approx. distance in m and interest level 0-5."


def get_client() -> OpenAI:
    global _client

    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set.")
        _client = OpenAI(api_key=api_key)

    return _client


def to_data_url(path: str) -> str:
    with open(path, "rb") as fh:
        return "data:audio/wav;base64," + base64.b64encode(fh.read()).decode("utf-8")


def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def multimodal_prompt(base64_img: str, base64_audio: str, model: str = "gpt-4o-mini") -> str:
    ai_response = get_client().responses.create(
        model="gpt-audio",
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{base64_img}",
                    },
                    {
                        "type": "input_audio",
                        "audio": f"data:audio/wav;base64,{base64_audio}",
                    },
                ],
            }
        ],
    )

    return ai_response.output_text


def transcribe_img(base64_img: str, model: str = "gpt-4o-mini", prompt: str = DEFAULT_PROMPT) -> str:
    ai_response = get_client().responses.create(
        model=model,
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{base64_img}",
                    },
                ],
            }
        ],
    )

    return ai_response.output_text


def strigalize_verb(path_to_audio_file: str, diarized: bool = False) -> str:
    with open(path_to_audio_file, "rb") as audio_file:
        if not diarized:
            transcript = get_client().audio.transcriptions.create(
                model="gpt-4o-transcribe",
                file=audio_file,
                temperature=0,
                chunking_strategy="auto",
            )
        else:
            transcript = get_client().audio.transcriptions.create(
                model="gpt-4o-transcribe-diarize",
                file=audio_file,
                chunking_strategy="auto",
            )
            for segment in transcript.segments:
                print(segment.speaker, segment.text, segment.start, segment.end)

    print(f"Detected: {transcript.text}")
    return transcript.text
