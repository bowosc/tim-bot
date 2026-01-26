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
def check_camera(focus: Optional[str] = None) -> str:
    '''
    Generates a description of what's in front of the robot, with an optional focus on a specific, already known object.

    :param Optional[str] focus: A specific object to get more information about. If focus is None, this function will describe the whole scene.
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
        ["rpicam-jpeg", "-o", "-nopreview", "--timeout", "1"],
        stdout = subprocess.PIPE,
        stderr = subprocess.DEVNULL,
        check = True
    )

    jpeg_bytes = result.stdout
    if not jpeg_bytes:
        raise RuntimeError("Camera returned an empty frame.")
    
    b64 = base64.b64encode(jpeg_bytes).decode("ascii")
    data_url = f"data:image/jpeg;base64,{b64}"

    #img_b64 = bob.get_jpeg_bytes()
    
    #with open("assets/1901.jpeg", "rb") as f:
    #    img_b64 = base64.b64encode(f.read()).decode("utf-8")

    # get img from response and feed it into transcription
    
    if (focus and len(focus) > 1):
        transcription = transcribe_img(
                base64_img=data_url, 
                prompt=f'''
                Generate a max-two-sentence detailed description focusing on only following part of this image: {focus}. 
                If you can\'t make anything out, return "Visibility too low."
                '''
            )
    else:
        transcription = transcribe_img(
                base64_img=data_url
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
    asyncio.run(tts_to_wav_file(phrase, instructions=f"Speak with the inflection: {inflection}"))
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