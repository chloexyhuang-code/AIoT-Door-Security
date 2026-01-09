# 智慧物聯網門禁警示系統
本專題為「門禁警示系統」，使用 Raspberry Pi 5、HC-SR501 人體感測器與MC-38 有線門感應磁性開關，當偵測到有人或門被打開時，會 LED 會亮並透過 AWS雲端 + LINE 通知使用者。
## 系統架構

- 邊緣端：Raspberry Pi 5 + 感測器 + LED
- 通訊協定：MQTT
- 雲端平台：AWS IoT Core、Lambda、DynamoDB
- 通知服務：LINE Notify
## 硬體設備

- Raspberry Pi 5
- HC-SR501 人體紅外線感測器
- MC-38 有線門磁感測器
- LED 燈
- 杜邦線
## GPIO 腳位

- HC-SR501 人體紅外線感測器 GPIO 17
- MC-38 有線門磁感測器 GPIO 27
- LED 燈 GPIO 22
## 檔案說明

- `main.py`：主程式，讀取感測器狀態、做邏輯判斷、控制 LED，並在偵測到異常時透過 LINE Messaging API 即時推播警示訊息到手機。
- `.env`：放置LINE、AWS的設定值。
- `MQTT_main.py`：MQTT 連線與訊息發布。
- `lambda_function.py`：AWS Lambda 雲端處理程式。
- `test_HC-SR501.py`：人體感測器測試程式。
- `requirements.txt`：所需的Python套件。
- `mqtt.py`：在樹莓派上讀取人體紅外線感測器和門磁開關的狀態，並把結果透過 MQTT 上傳到 AWS IoT Core。
## 專題成果

- 偵測門前是否有人與門是否被打開，若是有人或者門被打開，本地端 LED 燈會亮
- 事件資料可上傳至 AWS 雲端
- LINE 即時傳訊息至官方帳號通知使用者



