import RPi.GPIO as GPIO
import time

PIR_PIN = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)

print("HC-SR501 測試開始，請在感測器前移動...")

try:
    while True:
        if GPIO.input(PIR_PIN):
            print("motion")
            time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()
    print("結束 HC-SR501 測試")
