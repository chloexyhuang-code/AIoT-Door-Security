import os
import json
import boto3
import urllib3
from datetime import datetime

http = urllib3.PoolManager()
dynamodb = boto3.resource("dynamodb")

PUSH_ENDPOINT = "https://api.line.me/v2/bot/message/push"


def push_line(token: str, to: str, text: str):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    body = {
        "to": to,
        "messages": [{"type": "text", "text": text}],
    }

    resp = http.request(
        "POST",
        PUSH_ENDPOINT,
        body=json.dumps(body).encode("utf-8"),
        headers=headers,
        timeout=10.0,
    )

    return resp.status, resp.data.decode("utf-8")


def lambda_handler(event, context):
    # event 通常就是 IoT Rule 傳來的 payload（JSON）
    table_name = os.getenv("TABLE_NAME", "DoorEvents")
    token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")
    line_to = os.getenv("LINE_TO", "")

    table = dynamodb.Table(table_name)

    device_id = event.get("deviceId", "unknown")
    ts = event.get("ts") or datetime.utcnow().isoformat()
    motion = bool(event.get("motion"))
    door_open = bool(event.get("doorOpen"))
    alert = bool(event.get("alert", True))

    # 1) 寫入 DynamoDB
    item = {
        "pk": f"DEVICE#{device_id}",
        "sk": f"TS#{ts}",
        "deviceId": device_id,
        "ts": ts,
        "motion": motion,
        "doorOpen": door_open,
        "alert": alert,
        "raw": event,  # 保留原始資料（加分）
    }
    table.put_item(Item=item)

    # 2) LINE 推播
    parts = []
    if motion:
        parts.append("🚶 偵測到門前有人")
    if door_open:
        parts.append("🚪 門已被打開")

    msg = "⚠️ 入侵警示\n" + "\n".join(parts) + f"\n時間：{ts}\n裝置：{device_id}"

    if token and line_to:
        status, data = push_line(token, line_to, msg)
        return {"ok": True, "line_status": status, "line_response": data}

    return {"ok": True, "note": "Saved to DynamoDB, but LINE env vars not set."}
