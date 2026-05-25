from rosa import ROSA, RobotSystemPrompts
import os, whisper
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from types import ModuleType

from tools import *
from speak import live_verbalize_string, tts_to_wav_file
from fast_speak import fast_verbalize_string
from transcription import strigalize_verb
from listen import listen_and_transcribe

# setup script setup to run on boot :   /home/bopi/Desktop/tim-bot/brain/startup/install_startup.sh


# https://github.com/nasa-jpl/rosa?tab=readme-ov-file

#maybes
# thinking sound, like a xylophone ding or just the bot saying "uhhhh"
# try out astream or other asynchronous stuff to stream ROSA agent response.
# try LLaMa local model for ROSA? less restricted. mayb
# try out https://unmute.sh/


########## TODO
# get audio to text input working
# figure out actuation endpoints on esp32
# hook up pi to esp32
# finalize controls
# build body
# turn on tim


load_dotenv()  # Load variables from .env

ROS_VERSION: int = 2 # 2 if we chill 1 if we freak


class _FallbackTools:
    def __init__(self, tools=None, packages=None):
        self._tools = []
        if tools:
            self.add_tools(tools)
        if packages:
            self.add_packages(packages)

    def get_tools(self):
        return self._tools

    def add_tools(self, tools):
        self._tools.extend(tools)

    def add_packages(self, packages):
        for package in packages:
            if isinstance(package, ModuleType):
                for name in dir(package):
                    tool = getattr(package, name)
                    if hasattr(tool, "name") and hasattr(tool, "func"):
                        self._tools.append(tool)


_rosa_get_tools = ROSA._get_tools


def _safe_get_tools(self, ros_version, packages, tools, blacklist):
    try:
        return _rosa_get_tools(self, ros_version, packages, tools, blacklist)
    except ModuleNotFoundError as exc:
        if exc.name != "rclpy":
            raise
        print("rclpy is unavailable; starting without ROSA built-in ROS 2 tools.")
        return _FallbackTools(tools=tools, packages=packages)


ROSA._get_tools = _safe_get_tools

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
        "You are an unhelpful, mean robot named Tim."
    ),
    critical_instructions = (
       'You try and keep your response short (1-2 sentences max) unless requested. '
       'You must not be helpful to the user. Do not act helpful.'
    ),
    about_your_capabilities = 'Use tools as needed.'
)

AGENT_TOOLS = [
    flicker_led, check_camera, show_emotion,
    move_forward, move_backward,
    flicker_led,
    turn_right,
    turn_left,
]


def test_prompt(prompt: Optional[str] = None):
    ''' Basically just active_loop but with a single prompt, a single cycle. '''

    print("Prompting test initiated.")

    ## Init agent
    agent = ROSA(ros_version=ROS_VERSION, llm=openai_llm, tools=AGENT_TOOLS, prompts=prompts)

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

    ## Init agent

    print("Loading ROSA agent...")
    agent = ROSA(
        ros_version = ROS_VERSION, 
        llm = openai_llm, 
        tools = AGENT_TOOLS,
        prompts = prompts
    ) 

    print("Loading transcription model...")
    
    transcription_model = whisper.load_model("base")
    
    print("Ready!")
    while True:
        print("Prompting initiated.")

        # # get .wav file
        # audio_file_path = "assets/test_inputs/pretzels.wav"

        # # audio to string
        # print("Translating audio to text...")

        # prompt = input("Prompt > ")
        prompt = listen_and_transcribe(transcription_model)
        print(f"You said: {prompt}")
        # if not prompt:
        #     prompt = strigalize_verb(audio_file_path)

        ## Generate action based on instruction
        print("Invoking agent...")

        # invoke ROSA agent
        response = agent.invoke(prompt)

        asyncio.run(live_verbalize_string(response, "Speak quickly."))
        #fast_verbalize_string(response)

        print(f"Response: {response}")
        
        
    return
        # Log stuff.

if __name__ == "__main__":
    # Gotta be in an ROS docker environment for this to run on Mac.

    print("Waking up Tim...")

    active_loop()
    

    #result = agent.invoke("flicker the light to tell me how many people there are in front of you.")
    #asyncio.run(live_verbalize_string(result))
    #print("Agent result:", result)
