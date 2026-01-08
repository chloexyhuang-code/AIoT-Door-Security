import os
import json
import time
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

from gpiozero import MotionSensor, Button, LED
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

# GPIO (BCM)
PIR_PIN = 17
DOOR_PIN = 27
LED_PIN = 22

COOLDOWN_SECONDS = 10  # 避免一直 publish

TZ = timezone(timedelta(hours=8))  # Taiwan +08:00


def iso_ts():
    return datetime.now(TZ).isoformat(timespec="seconds")


def build_client(endpoint, client_id, root_ca, cert, key):
    c = AWSIoTMQTTClient(client_id)
    c.configureEndpoint(endpoint, 8883)
    c.configureCredentials(root_ca, key, cert)

    # 穩定性設定（很重要）
    c.configureAutoReconnectBackoffTime(1, 32, 20)
    c.configureOfflinePublishQueueing(-1)  # 無限 queue
    c.configureDrainingFrequency(2)
    c.configureConnectDisconnectTimeout(10)
    c.configureMQTTOperationTimeout(5)
    return c


def main():
    load_dotenv()

    endpoint = os.getenv("AWS_IOT_ENDPOINT", "").strip()
    client_id = os.getenv("AWS_IOT_CLIENT_ID", "pi5-door-01").strip()
    topic = os.getenv("AWS_IOT_TOPIC", "iot/door/pi5-door-01/events").strip()

    root_ca = os.getenv("AWS_IOT_ROOT_CA", "").strip()
    cert = os.getenv("AWS_IOT_CERT", "").strip()
    key = os.getenv("AWS_IOT_PRIVATE_KEY", "").strip()

    if not all([endpoint, root_ca, cert, key]):
        raise RuntimeError("Pi 端 .env 缺 AWS_IOT_ENDPOINT / ROOT_CA / CERT / PRIVATE_KEY")

    pir = MotionSensor(PIR_PIN)
    door = Button(DOOR_PIN, pull_up=True)
    led = LED(LED_PIN)

    client = build_client(endpoint, client_id, root_ca, cert, key)
    if not client.connect():
        raise RuntimeError("MQTT connect failed")

    print("✅ Connected to AWS IoT Core")
    print(f"Topic: {topic}")

    last_sent = 0.0
    last_motion = False
    last_door_open = False

    while True:
        motion = pir.motion_detected
        door_open = not door.is_pressed  # 常見接法：開門=True

        alert = motion or door_open
        led.value = 1 if alert else 0

        changed = (motion != last_motion) or (door_open != last_door_open)
        now = time.time()

        if alert and changed and (now - last_sent >= COOLDOWN_SECONDS):
            payload = {
                "deviceId": client_id,
                "ts": iso_ts(),
                "motion": bool(motion),
                "doorOpen": bool(door_open),
                "alert": True,
                "note": "motion OR doorOpen",
            }
            client.publish(topic, json.dumps(payload, ensure_ascii=False), 1)
            print("Published:", payload)
            last_sent = now

        last_motion = motion
        last_door_open = door_open
        time.sleep(0.2)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Stopped.")
