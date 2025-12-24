from openai import OpenAI
from dotenv import load_dotenv
import os, base64

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

DEFAULT_PROMPT = "Give me a short list of objects in this image, seperated by commas."
JSON_PROMPT = "Generate json data for each object in this image, including approx. distance in m and interest level 0-5."


def to_data_url(path: str) -> str:
    with open(path, "rb") as fh:
        return "data:audio/wav;base64," + base64.b64encode(fh.read()).decode("utf-8")


def multimodal_prompt(base64_img: str, base64_audio: str, model: str = "gpt-4o-mini") -> str:
    '''
    Generates a transcription describing the content of an image and an audio input by calling the OpenAI API.

    :param str base64_img: Base64 string of the image.
    :param str base64_audio: Base64 string of the audio.
    :param str model: OpenAI model to process image and prompt.
    :return str: Transcription of the image.
    '''

    ai_response = client.responses.create(
        model="gpt-audio", # idk
        input=[
            {
                "role": "user",
                "content": [
                    #{ "type": "input_text", "text": prompt },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{base64_img}",
                    },
                    { 
                        "type": "input_audio", 
                        "audio": f"data:audio/wav;base64,{base64_audio}"
                    }
                ],
            }
        ],
    )

    return ai_response.output_text

def transcribe_img(base64_img: str, model: str = "gpt-4o-mini", prompt: str = DEFAULT_PROMPT) -> str:
    '''
    Generates a transcription describing the content of an image by calling the OpenAI API.

    :param str base64_img: Base64 string of the image.
    :param str model: OpenAI model to process image and prompt.
    :param str prompt: Prompt to send to API along with the image.
    :return str: Transcription of the image.
    '''

    ai_response = client.responses.create(
        model=model,
        input=[
            {
                "role": "user",
                "content": [
                    { "type": "input_text", "text": prompt },
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

        if not diarized: # default, one speaker
            transcript = client.audio.transcriptions.create(
                model="gpt-4o-transcribe",
                file=audio_file,
                temperature=0,
                chunking_strategy="auto"
            )
        else: # multiple speakers
            transcript = client.audio.transcriptions.create(
                model="gpt-4o-transcribe-diarize",
                file=audio_file,
                #response_format="diarized_json",
                chunking_strategy="auto",
                # extra_body={
                #     "known_speaker_names": ["Kramer", "Jerry"], # max 4 ppl
                #     "known_speaker_references": [to_data_url("assets/pretzels.wav"), to_data_url("assets/jerry_sample.wav")],
                # },
            )
            for segment in transcript.segments:
                print(segment.speaker, segment.text, segment.start, segment.end)


    print(f"Detected: {transcript.text}")

    return transcript


if __name__ == "__main__":

    image_path = "assets/1901.jpeg"

    #print(transcribe_img(image_path))
    strigalize_verb("assets/write-off.wav")
    

# def encode_image(image_path: str) -> str:
#     '''
#     Image to Base64
#     :param str image_path: Path to the image.
#     :return str: Base64 string of the image.
#     '''
#     with open(image_path, "rb") as image_file:
#         return base64.b64encode(image_file.read()).decode("utf-8")
