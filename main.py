#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import requests
from datetime import datetime
from dotenv import load_dotenv
from gpiozero import MotionSensor, Button, LED

# ----------------------------
# GPIO (BCM)
# ----------------------------
PIR_PIN = 17       # HC-SR501 OUT
DOOR_PIN = 27      # Door magnetic switch
LED_PIN = 22       # LED (+ resistor)

# 避免一直發訊息
COOLDOWN_SECONDS = 20

# LINE Push API endpoint 
PUSH_ENDPOINT = "https://api.line.me/v2/bot/message/push"


def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def send_text_message(channel_access_token: str, to: str, text: str) -> bool:
    """
    呼叫 LINE Messaging API Push API 送出文字訊息
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {channel_access_token}",
    }
    body = {
        "to": to,
        "messages": [{"type": "text", "text": text}],
    }

    try:
        resp = requests.post(PUSH_ENDPOINT, headers=headers, json=body, timeout=10)
        if resp.status_code == 200:
            return True
        print(f"[LINE] 送出失敗 status={resp.status_code}")
        print(f"[LINE] response={resp.text}")
        return False
    except requests.RequestException as e:
        print(f"[LINE] Request error: {e}")
        return False


def main():
    # 讀取 .env
    load_dotenv()
    channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "").strip()
    user_id = os.getenv("LINE_USER_ID", "").strip()

    if not channel_access_token or not user_id:
        print("請先在 .env 中設定 LINE_CHANNEL_ACCESS_TOKEN 和 LINE_USER_ID")
        sys.exit(1)

    # 初始化 GPIO
    pir = MotionSensor(PIR_PIN)
    door = Button(DOOR_PIN, pull_up=True)  # 內建上拉
    led = LED(LED_PIN)

    last_sent = 0.0
    last_motion = False
    last_door_open = False

    print("✅ System started")
    print(" - PIR: motion_detected")
    print(" - Door: door_open = not door.is_pressed (pull_up=True)")
    print(" - LED: ON if motion OR door_open")
    print("Press Ctrl+C to stop.\n")

    # 開機通知
    send_text_message(
        channel_access_token,
        user_id,
        f"✅ 物聯網門禁系統已啟動\n時間：{now_str()}"
    )

    try:
        while True:
            motion = pir.motion_detected

            # 常見門磁接法：關門時磁簧閉合 -> 拉到GND -> is_pressed=True
            door_open = not door.is_pressed

            # LED 控制：有人 or 門開 就亮
            if motion or door_open:
                led.on()
            else:
                led.off()

            # 狀態變化才通知（避免每0.2秒發一次）
            changed = (motion != last_motion) or (door_open != last_door_open)

            if changed and (motion or door_open):
                now = time.time()
                if now - last_sent >= COOLDOWN_SECONDS:
                    parts = []
                    if motion:
                        parts.append("🚶 偵測到門前有人")
                    if door_open:
                        parts.append("🚪 門已被打開")

                    msg = "⚠️ 入侵警示\n" + "\n".join(parts) + f"\n時間：{now_str()}"

                    ok = send_text_message(channel_access_token, user_id, msg)
                    if ok:
                        print(f"[{now_str()}] LINE pushed: {parts}")
                        last_sent = now

            last_motion = motion
            last_door_open = door_open

            time.sleep(0.2)

    except KeyboardInterrupt:
        led.off()
        print("\n🛑 Stopped.")


if __name__ == "__main__":
    main()
