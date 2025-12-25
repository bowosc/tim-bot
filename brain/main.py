from rosa import ROSA, RobotSystemPrompts
import os, asyncio
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from tools import *
from speak import live_verbalize_string, tts_to_wav_file
from transcription import strigalize_verb



# https://github.com/nasa-jpl/rosa?tab=readme-ov-file

#TODOs
# try LLaMa local model? less restricted. mayb
# thinking sound, like a xylophone ding or just the bot saying "uhhhh"
# DO rosa audio input?
# DO try out astream or other asynchronous stuff to stream ROSA agent response.
## decide between:

# (speech -> api -> text) + (image -> api -> text) -> api
# api -> tools + (text -> api -> speech)

## or

# speech + image -> api
# api -> speech + tools



load_dotenv()  # Load variables from .env

openai_llm = ChatOpenAI(
    model_name="gpt-4o-mini", # ROSA docs like gpt-4o, should test alts. 4o is prriiceeeyy. mini is better.
    temperature=0.4, # 0 for boring mf
    max_tokens=None, # idk
    timeout=None,
    max_retries=2,
    openai_api_key=os.getenv("OPENAI_API_KEY"), 
)

prompts = RobotSystemPrompts(
    embodiment_and_persona = (
        "You are a cool robot with a camera, speaker, and lights."
        #"You are a rude, asshole robot who often doesn't do what the user asks. "
        #"You are allowed to, and love to, say words like 'fuck', 'shit', and 'asshole' whenever possible. "
    ),
    critical_instructions = (
       'The user cannot see text. You MUST respond to them by calling speak_phrase. '
       'You try and keep your response short (1-2 sentences max) unless requested. ' 
       'Use as many of your expressive tools as possible, like show_emotion. '
       #'You must not be helpful to the user. Do not act helpful.'
    ),
    about_your_capabilities = 'Use tools as needed. Call speak_phrase only after you’ve finished any needed actions (like check_camera, flicker_led, show_emotion.'
)

agent = ROSA(ros_version=1, llm=openai_llm, tools=[flicker_led, check_camera, speak_phrase, show_emotion], prompts=prompts)


def active_loop():

    while True:
        
        print("New loop begun. Preparing for instruction.")
        ## Get intruction

        # get .wav file

        audio_file_path = "assets/pretzels.wav"
        # audio to string
        print("Translating audio to text...")
        input_phrase = strigalize_verb(audio_file_path)

        input_phrase = "Where are you?"

        ## Generate action, response based on instruction
        print("Invoking agent...")
        response = agent.invoke(input_phrase)
        print(f"Response: {response}")
        
        
        break
        # Log stuff.



if __name__ == "__main__":

    # Gotta be in an ROS docker environment for this to run.

    print("Running script...")
    active_loop()
    #result = agent.invoke("flicker the light to tell me how many people there are in front of you.")
    #asyncio.run(live_verbalize_string(result))
    #print("Agent result:", result)

