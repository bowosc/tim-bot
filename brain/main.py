from rosa import ROSA, RobotSystemPrompts
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from tools import flicker_led, check_camera

# https://github.com/nasa-jpl/rosa?tab=readme-ov-file

#TODOs
# try LLaMa local model? less restricted. mayb
# how can I get an audio response from the openai api by inputting audio and images?
# thinking sound, like a xylophone ding or just the bot saying "uhhhh"
# DO rosa audio input.
# DO try out astream, asynchronously stream ROSA agent response.
## decide between:

# (speech -> api -> text) + (image -> api -> text) -> api
# api -> tools + (text -> api -> speech)

## or

# speech + image -> api
# api -> speech + tools



load_dotenv()  # Load variables from .env

openai_llm = ChatOpenAI(
    model_name="gpt-4o-mini", # ROSA docs like gpt-4o, should test alts. this mf is prriiceeeyy.
    temperature=0, # boring mf
    max_tokens=1000000, # idk seems like enough
    timeout=None,
    max_retries=2,
    openai_api_key=os.getenv("OPENAI_API_KEY"),  # Use env var
)

prompts = RobotSystemPrompts(
    embodiment_and_persona="You are a robot that has an LED light and a camera."
)

agent = ROSA(ros_version=1, llm=openai_llm, tools=[flicker_led, check_camera], prompts=prompts)



def active_loop():

    while True:
        
        # Get intruction

        # Generate action, response based on instruction
        result = agent.invoke()

        # Log stuff.



if __name__ == "__main__":

    # Gotta be in an ROS docker environment for this to run.

    print("Running script...")
    result = agent.invoke("flicker the light to tell me how many apples there are in front of you.")
    print("Agent result:", result)
