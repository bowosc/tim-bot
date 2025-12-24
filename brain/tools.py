from langchain.agents import tool
from comms import send_cmd
from transcription import transcribe_img
from typing import Optional
import time, base64

from audio import text_to_speech, speech_to_text

@tool(description="Toggles the blue LED on/off every 0.5 seconds for a certain amount of time.")
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

@tool(description="Generates a description of what's in front of the robot, with an optional focus on a specific, already known object.")
def check_camera(focus: Optional[str]) -> str:
    '''
    Generates a description of what's in front of the robot, with an optional focus on a specific, already known object.

    :param Optional[str] focus: A spec0ific object to get more information about. If focus is None, this function will describe the whole scene.
    :return str: A description of what the camera sees.
    '''

    return "A table with a salt shaker, a glass of water, and a bowl of pretzels. A man is holding a pretzel."
    #return "A blank white room with three apples on the ground in front of you."

    # Get img from esp32, convert to base64 so gpt can read it.
    resp = send_cmd("/checkcamera")
    img_b64 = base64.b64encode(resp.content).decode("utf-8")

    # get img from response and feed it into transcription

    if (focus and len(focus) > 1):
        transcription = transcribe_img(
                base64_img=img_b64, 
                prompt=f"Generate a max-two-sentence description of the following part of this image: {focus}"
            )
    else:
        transcription = transcribe_img(
                base64_img=img_b64
            )
    
    return transcription

@tool("Verbally state a phrase string with a described inflection.")
def verbalize_string(phrase: str, inflection: str) -> None:
    '''
    Verbally state a string out loud with a described inflection, via TTS.
    
    :param str phrase: The phrase to be spoken aloud.
    :param str inflection: How you want the phrase to be spoken, e.g. sarcastically, matter-of-fact, humorously.
    :return None:
    '''

    # make audio file
    audio_file_path = text_to_speech(phrase, inflection)
    
    # tell esp32 to say it
    # send_cmd()


    return


### Movement ###

@tool("Moves the robot forward a specified amount. The distance can be negative, to move backwards.")
def move_forward(distance: int, speed: int) -> None:
    '''
    Moves the robot forward a specified amount. The distance can be negative, to move backwards.

    
    :param int distance: How far to move forward, in meters. This value can be negative.
    :param int speed: How quickly to move, on a scale of 1 to 5.
    :return None:
    '''

    return

@tool
def turn(degrees: int, speed: int) -> None:
    '''
    Turns the robot a specified amount.

    :param int degrees: How many degrees to turn, negative being clockwise and positive being counterclockwise.
    :param int speed: How quickly to turn, on a scale of 1 to 5. Note that faster turns may be less precise.
    :return None:
    '''

    return