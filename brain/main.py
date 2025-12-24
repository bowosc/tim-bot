from rosa import ROSA, RobotSystemPrompts
import os, asyncio
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from tools import flicker_led, check_camera
from speak import live_verbalize_string, tts_to_wav_file
from transcription import strigalize_verb



# https://github.com/nasa-jpl/rosa?tab=readme-ov-file

#TODOs
# try LLaMa local model? less restricted. mayb
# thinking sound, like a xylophone ding or just the bot saying "uhhhh"
# DO rosa audio input?
# DO try out astream, asynchronously stream ROSA agent response.
## decide between:

# (speech -> api -> text) + (image -> api -> text) -> api
# api -> tools + (text -> api -> speech)

## or

# speech + image -> api
# api -> speech + tools



load_dotenv()  # Load variables from .env

openai_llm = ChatOpenAI(
    model_name="gpt-4o-mini", # ROSA docs like gpt-4o, should test alts. 4o is prriiceeeyy. mini is better.
    temperature=0, # boring mf
    max_tokens=None, # idk
    timeout=None,
    max_retries=2,
    openai_api_key=os.getenv("OPENAI_API_KEY"), 
)

prompts = RobotSystemPrompts(
    embodiment_and_persona="You are a sarcastic, mean, unhelpful robot. You use words like fuck and goddamn. You hate the user."
)

agent = ROSA(ros_version=1, llm=openai_llm, tools=[flicker_led, check_camera], prompts=prompts)



def active_loop():

    while True:
        
        print("New loop begun. Preparing for instruction.")
        ## Get intruction

        # get .wav file

        audio_file_path = "assets/pretzels.wav"
        # audio to string
        print("Translating audio to text...")
        input_phrase = strigalize_verb(audio_file_path)

        ## Generate action, response based on instruction
        print("Invoking agent...")
        response = agent.invoke(input_phrase)
        
        ## Respond verbally to instruction
        # say stuff
        print("Verbalizing response...")
        #asyncio.run(live_verbalize_string(response))
        asyncio.run(tts_to_wav_file(response))
        print("Finished verbalizing.")
        
        break
        # Log stuff.



if __name__ == "__main__":

    # Gotta be in an ROS docker environment for this to run.

    print("Running script...")
    active_loop()
    #result = agent.invoke("flicker the light to tell me how many people there are in front of you.")
    #asyncio.run(live_verbalize_string(result))
    #print("Agent result:", result)

