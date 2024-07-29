import serial
import time

try:
    arduino = serial.Serial(port="COM5", baudrate=115200, timeout=.1)
except Exception as e:
    print(f"Error opening serial port: {e}")
    exit()

while True:
    try:
        arduino.write(bytes("Green\n", 'utf-8'))  # Append newline character
        time.sleep(20)
    except Exception as e:
        print(f"Error writing to serial port: {e}")
