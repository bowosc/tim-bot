import os

import serial


SERIAL_PORT = os.getenv("TIM_BOT_SERIAL_PORT", "/dev/ttyUSB0")
SERIAL_BAUDRATE = int(os.getenv("TIM_BOT_SERIAL_BAUDRATE", "115200"))
_serial_connection = None


def _get_serial_connection() -> serial.Serial:
    global _serial_connection

    if _serial_connection is None:
        _serial_connection = serial.Serial(
            port=SERIAL_PORT,
            baudrate=SERIAL_BAUDRATE,
            timeout=0.1,
        )

    return _serial_connection


def send_serial_command(cmd: str) -> None:
    ser = _get_serial_connection()
    print("Sent to esp32: ", cmd)
    ser.write(cmd.encode())

    line = ser.readline().decode().strip()
    if line:
        print("ESP32 says:", line)
