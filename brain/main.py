from rosa import ROSA, RobotSystemPrompts
import os, time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import tool

from comms import send_cmd

# https://github.com/nasa-jpl/rosa?tab=readme-ov-file

load_dotenv()  # Load variables from .env

openai_llm = ChatOpenAI(
    model_name="gpt-5-nano", # ROSA docs like gpt-4o, should test alts. this mf is prriiceeeyy.
    temperature=0, # boring mf
    max_tokens=None,
    timeout=None,
    max_retries=2,
    openai_api_key=os.getenv("OPENAI_API_KEY"),  # Use env var
)

# @tool
# def descriptive_tool_name(param1: type1, param2: type2) -> str:
#     """
#     Description of the tool.
    
#     :param param1: Description of param1 and how it is used.
#     :param param2: Description of param2 and how it is used.
#     """
#     # Your code here ...
#     return f"Action taken: {ACTION}, retrieved data: {DATA}."

@tool
def flicker_led(duration: int = 2) -> str:
    """
    Toggles the blue LED on/off every 0.5 seconds for a certain amount of time.
    
    :param int duration: How long (in seconds) to flicker the LED for.
    """

    print("Starting to flicker LED.")
    for i in range(duration):
        send_cmd("on")
        time.sleep(0.5)
        send_cmd("off")
        time.sleep(0.5)

    print("Finished flickering LED.")

    return f"Flickering LED for {duration} seconds."


prompts = RobotSystemPrompts(
    embodiment_and_persona="You are a cool robot that has an LED light."
)

agent = ROSA(ros_version=1, llm=openai_llm, tools=[flicker_led], prompts=prompts)

if __name__ == "__main__":

    # Gotta be in an ROS docker environment for this to run.

    print("Running script...")
    result = agent.invoke("flicka that light brother")
    print("Agent result:", result)