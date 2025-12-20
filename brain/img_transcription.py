from openai import OpenAI
from dotenv import load_dotenv
import os, base64

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)



DEFAULT_PROMPT = "Give me a short list of objects in this image, seperated by commas."

def encode_image(image_path: str) -> str:
    '''
    Image to Base64
    
    :param str image_path: Path to the image.
    :return str: Base64 string of the image.
    '''

    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def transcribe_img(img_path: str, model: str = "gpt-4o-mini", prompt: str = DEFAULT_PROMPT) -> str:
    
    # get the Base64 string bc easier for openai
    base64_image = encode_image(img_path)

    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {
                "role": "user",
                "content": [
                    { "type": "input_text", "text": DEFAULT_PROMPT },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{base64_image}",
                    },
                ],
            }
        ],
    )

    return response.output_text

if __name__ == "__main__":

    image_path = "assets/1901.jpeg"

    print(transcribe_img(image_path))
    
