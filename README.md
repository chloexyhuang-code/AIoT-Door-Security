# AIoT-Door-Security
本專題為「智慧物聯網門禁警示系統」，使用 Raspberry Pi 5、HC-SR501 人體感測器與MC-38 有線門感應磁性開關，當偵測到有人或門被打開時，會 LED 會亮並透過 AWS雲端 + LINE 通知使用者。

## 系統架構

- 邊緣端：Raspberry Pi 5 + 感測器 + LED
- 通訊協定：MQTT
- 雲端平台：AWS IoT Core、Lambda、DynamoDB
- 通知服務：LINE Notify

硬體接線說明：HC-SR501 接到 GPIO 17；門磁開關接到 GPIO 27；LED 接到 GPIO 22
