import RPi.GPIO as GPIO
import time
import json
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from datetime import datetime

# ===== GPIO 設定 =====
PIR_PIN = 17      # HC-SR501
DOOR_PIN = 27     # 門磁開關

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)
GPIO.setup(DOOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# ===== AWS IoT MQTT 設定 =====
client = AWSIoTMQTTClient("rpi5-16")

client.configureEndpoint(
    "a13a5hbzjfyrzt-ats.iot.us-east-1.amazonaws.com", 8883
)

client.configureCredentials(
    "/home/abc/workspace/final/certs2/Amazon-root-CA-1.pem",
    "/home/abc/workspace/final/certs2/private.pem.key",
    "/home/abc/workspace/final/certs2/device.pem.crt"
)

client.configureOfflinePublishQueueing(-1)
client.configureDrainingFrequency(2)
client.configureConnectDisconnectTimeout(10)
client.configureMQTTOperationTimeout(5)

client.connect()


TOPIC = "home/security"

print("系統啟動，開始監測...")

try:
    while True:
        pir_state = GPIO.input(PIR_PIN)
        door_state = GPIO.input(DOOR_PIN)

        data = {
            "device_id": "home01",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "HC-SR501": "motion" if pir_state else "no_motion",
            "door": "open" if door_state == GPIO.LOW else "closed"
        }

        client.publish(TOPIC, json.dumps(data), 1)
        print("已發送：", data)

        time.sleep(3)

except KeyboardInterrupt:
    GPIO.cleanup()
    print("系統停止")
