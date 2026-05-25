from langchain.agents import tool
from webcomms import send_cmd
from transcription import transcribe_img, to_data_url
from typing import Optional
import time, base64, asyncio, subprocess
from speak import live_verbalize_string, tts_to_wav_file
from fast_speak import fast_verbalize_string
# from pi_cam import PiCamera2Backend

# bob = PiCamera2Backend()

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
def check_camera(focus: Optional[str] = None, quality: int = 40) -> str:
    '''
    Generates a description of what's in front of the robot, with an optional focus on a specific, already known object.

    :param Optional[str] focus: A specific object to get more information about. If focus is None, this function will describe the whole scene.
    :param int quality: 1-100, quality of image taken.
    :return str: A description of what the camera sees.
    '''
    print("Checking camera...")
    if focus:
        print(f"Focusing on {focus}...")

    #return "A table with a salt shaker, a glass of water, and a bowl of pretzels. A man is holding a pretzel."
    #return "A blank white room with three apples on the ground in front of you."

    # Get img from esp32, convert to base64 so gpt can read it.
    

    # ################### ESP32 version
    # resp = send_cmd("capture", timeout=6)
    
    # img_b64 = base64.b64encode(resp.content).decode("utf-8")
    # ####################

    result = subprocess.run(
        ["rpicam-jpeg", "--nopreview", "--timeout", "1500", "-q", f"{quality}", "-o", "-"],
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
        check = True
    )

    jpeg_bytes = result.stdout
    if not jpeg_bytes:
        raise RuntimeError("Camera returned an empty frame.")
    
    img_b64 = base64.b64encode(jpeg_bytes).decode("ascii")
    
    #with open("assets/1901.jpeg", "rb") as f:
    #    img_b64 = base64.b64encode(f.read()).decode("utf-8")

    # get img from response and feed it into transcription
    
    if (focus and len(focus) > 1):
        transcription = transcribe_img(
                base64_img=img_b64, 
                prompt=f'''
                Generate a max-two-sentence detailed description focusing on only following part of this image: {focus}. 
                If you can\'t make anything out, return "Visibility too low."
                '''
            )
    else:
        transcription = transcribe_img(
                base64_img=img_b64
            )
    
    print(f"Camera sees: {transcription}")
    return transcription

@tool(description="Verbally state a phrase string aloud with a described inflection.")
def speak_phrase(phrase: str, inflection: str) -> None:
    '''

    Verbally state a string out loud with a described inflection, via TTS.
    
    :param str phrase: The phrase to be spoken aloud.
    :param str inflection: How you want the phrase to be spoken, e.g. rudely, matter-of-fact, humorously.
    :return None:
    '''

    # make audio file
    
    print("Verbalizing response...")
    #TRYTHIS: asyncio.run(live_verbalize_string(response))
    #asyncio.run(tts_to_wav_file(phrase, instructions=f"Speak with the inflection: {inflection}"))
    fast_verbalize_string(phrase)

    print(f"Said: {phrase}")
    print(f"Inflection (not used): {inflection}")
    print("Finished verbalizing.")
    
    return

@tool(description="Show an emotion using your face.")
def show_emotion(emotion: str) -> None:
    '''
    Show a given emotion via various lights and gizmos (the LCD screen).

    :param str emotion: The emotion to show.
    :return None:
    '''
    print(f"Showing emotion: {emotion}")
    return






### ESP32 Controls ###

@tool(description="Moves the robot forward for 500ms.")
def move_forward() -> None:
    '''
    Moves the robot forward for 500ms.

    :return None:
    '''
    print("Sending move_forward command.")
    send_cmd("move_forward")
    return


@tool(description="Moves the robot backward for 500ms.")
def move_backward() -> None:
    '''
    Moves the robot backward for 500ms.

    :return None:
    '''
    print("Sending move_backward command.")
    send_cmd("move_backward")
    return


@tool(description="Turns the robot 90 degrees right.")
def turn_right() -> None:
    '''
    Turns the robot 90 degrees right.

    :return None:
    '''
    print("Sending turn_right command.")
    send_cmd("turn_right")
    return

@tool(description="Turns the robot 90 degrees left.")
def turn_left() -> None:
    '''
    Turns the robot 90 degrees left.

    :return None:
    '''
    print("Sending turn_left command.")
    send_cmd("turn_left")
    return

@tool(description="Flickers LED on and off for one second.")
def flicker_led() -> None:
    '''
    Flickers the LED on the robot for one second.

    :return None:
    '''
    print("Sending flicker_led pseudocommand.")

    send_cmd("led_on")
    time.sleep(0.2)
    send_cmd("led_off")
    time.sleep(0.2)
    send_cmd("led_on")
    time.sleep(0.2)
    send_cmd("led_off")
    time.sleep(0.2)
    send_cmd("led_on")
    time.sleep(0.2)
    send_cmd("led_off")
    return
