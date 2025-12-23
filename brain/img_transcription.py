from openai import OpenAI
from dotenv import load_dotenv
import os, base64

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

DEFAULT_PROMPT = "Give me a short list of objects in this image, seperated by commas."
JSON_PROMPT = "Generate json data for each object in this image, including approx. distance in m and interest level 0-5."


#TODO
# how can I get an audio response from the openai api by inputting audio and images?

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
        model="gpt-4o-mini",
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



def verabalize_string(phrase: str, voice: str = "alloy"):
    '''
    Generates an audio file verbalizing a given string and OpenAI voice.
    
    :param str phrase: The phrase to be converted to audio.
    :param str voice: A voice chosen from OpenAI's options.
    :return str: Path to the generated audio file.
    '''

    ## TODO: see if this actually works.

    completion = client.chat.completions.create(
        model="gpt-audio",
        modalities=["text", "audio"],
        audio={"voice": "alloy", "format": "wav"},
        messages=[
                {
                    "role": "user",
                    "content": phrase
                }
            ]
    )

    print(completion.choices[0])

    wav_bytes = base64.b64decode(completion.choices[0].message.audio.data)
    with open("assets/phrase_spoken.wav", "wb") as f:
        f.write(wav_bytes)

    return "assets/phrase_spoken.wav"


if __name__ == "__main__":

    image_path = "assets/1901.jpeg"

    print(transcribe_img(image_path))
    

# def encode_image(image_path: str) -> str:
#     '''
#     Image to Base64
#     :param str image_path: Path to the image.
#     :return str: Base64 string of the image.
#     '''
#     with open(image_path, "rb") as image_file:
#         return base64.b64encode(image_file.read()).decode("utf-8")
