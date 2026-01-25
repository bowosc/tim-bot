from __future__ import annotations
import time
from picamera2 import Picamera2

class PiCamera2Backend:
    def __init__(self):
        # import INSIDE so Mac never touches it
        self.picam2 = Picamera2()
        self.picam2.configure(self.picam2.create_still_configuration())
        self.picam2.start()
        time.sleep(0.5)

    def get_jpeg_bytes(self) -> bytes:
        return self.picam2.capture_buffer("main")

    def close(self) -> None:
        self.picam2.stop()
