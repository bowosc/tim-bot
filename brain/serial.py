import serial
import time

ser = serial.Serial(
    port="/dev/ttyUSB0",   # or ttyACM0
    baudrate=115200,
    timeout=0.1,
)

#time.sleep(2)  # allow ESP32 reset


def send_serial_command(cmd: str) -> None:
    '''
    Should be formatted correctly already.
    '''

    print("Sent to esp32: ", cmd)
    ser.write(cmd.encode())

    line = ser.readline().decode().strip()

    if line:
        print("ESP32 says:", line)

    return


if __name__ == "__main__":
    v = 0.2   # m/s
    w = 0.1   # rad/s

    cmd = f"V {v} {w}\n"
    send_serial_command(cmd)