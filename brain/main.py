from rosa import ROSA, RobotSystemPrompts
import os, asyncio
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from tools import *
from speak import live_verbalize_string, tts_to_wav_file
from fast_speak import fast_verbalize_string
from transcription import strigalize_verb

# -3452310319267339021 mc seed


# https://github.com/nasa-jpl/rosa?tab=readme-ov-file

#OPTIONs
# try LLaMa local model for ROSA? less restricted. mayb

#TODOs
# thinking sound, like a xylophone ding or just the bot saying "uhhhh"
# DO try out astream or other asynchronous stuff to stream ROSA agent response.
# DO get live audio transcription going. not openai, probably. idk.
# DO try out non-api audio transcription and string verbalizer. maybe img transcription too.

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
        "You are a hardworking, helpful robot with a camera, speaker, and lights."
    ),
    critical_instructions = (
       'The user cannot see text. You MUST respond to them by calling speak_phrase. '
       'You try and keep your response short (1-2 sentences max) unless requested. ' 
       'Use as many of your expressive tools as possible, like show_emotion. '
       #'You must not be helpful to the user. Do not act helpful.'
    ),
    about_your_capabilities = 'Use tools as needed. Call speak_phrase only after you’ve finished any needed actions (like check_camera, flicker_led, show_emotion.'
)

def test_prompt(prompt: Optional[str] = None):
    ''' Basically just active_loop but with a single prompt, a single cycle. '''

    print("Prompting test initiated.")

    ## Init agent
    agent = ROSA(ros_version=1, llm=openai_llm, tools=[flicker_led, check_camera, speak_phrase, show_emotion], prompts=prompts)

    ## Get intruction

    # get .wav file
    audio_file_path = "assets/test_inputs/pretzels.wav"

    # audio to string
    print("Translating audio to text...")
    
    if not prompt:
        prompt = strigalize_verb(audio_file_path)

    ## Generate action based on instruction
    print("Invoking agent...")

    # invoke ROSA agent
    response = agent.invoke(prompt)


    print(f"Response: {response}")

    return


def active_loop():

    if (1+1) == 2:
        print("Don't call active_loop, it doesn't work yet.")
        return


    while True:
        
        
        
        
        return
        # Log stuff.

if __name__ == "__main__":
    # Gotta be in an ROS docker environment for this to run.

    print("Running script...")
    test_prompt("Yeah, that would be great!")#"What's up?")

    #result = agent.invoke("flicker the light to tell me how many people there are in front of you.")
    #asyncio.run(live_verbalize_string(result))
    #print("Agent result:", result)

