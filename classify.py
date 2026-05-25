import RPi.GPIO as GPIO
import time
import subprocess
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model

# 設定 GPIO 腳位
SWITCH_PIN = 26  # 無段式按鈕 GPIO 腳位
GPIO.setmode(GPIO.BCM)
GPIO.setup(SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# 載入模型
model = load_model("/home/ken/trash_model.h5")

# 類別對應表
categories = ["Aluminium foil", "Paper", "Pet bottle"]
script_mapping = {
    "Aluminium foil": ("true90.py", "false90.py"),
    "Pet bottle": ("false90.py", "true90.py"),
    "Paper": ("true180.py", "true180.py")
}

# 開啟攝影機
cam = cv2.VideoCapture(0)  # 初始化攝影機

if not cam.isOpened():
    print("無法開啟攝影機")
    exit(1)

def classify_image(image):
    """使用模型進行影像分類"""
    image_resized = cv2.resize(image, (224, 224))  # 調整為模型輸入大小
    image_resized = np.array(image_resized) / 255.0  # 正規化
    image_resized = np.expand_dims(image_resized, axis=0)  # 增加 batch 維度
    predictions = model.predict(image_resized)
    class_index = np.argmax(predictions)
    return categories[class_index]

try:
    print("即時影像顯示中，等待按鈕按下進行分類...")
    
    while True:
        # 讀取即時影像
        ret, frame = cam.read()
        if not ret:
            print("影像擷取失敗")
            break
        
        # 顯示影像
        cv2.imshow("Live Camera", frame)

        # 按下按鈕進行分類
        if GPIO.input(SWITCH_PIN) == GPIO.LOW:
            print("按鈕按下，開始分類...")
            image_path = "/home/ken/test_images/captured.jpg"
            cv2.imwrite(image_path, frame)  # 儲存影像
            category = classify_image(frame)  # 影像分類
            print(f"分類結果: {category}")

            # 執行對應的腳本
            if category in script_mapping:
                script1, script2 = script_mapping[category]
                print(f"執行 {script1} ...")
                subprocess.Popen(["python3", script1])

                time.sleep(5)  # 等待 5 秒

                print(f"執行 {script2} ...")
                subprocess.Popen(["python3", script2])

            print("等待下一次按鈕觸發...")

        # 按下 'q' 離開程式
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("程式終止，清理資源...")
finally:
    cam.release()  # 釋放攝影機
    cv2.destroyAllWindows()  # 關閉視窗
    GPIO.cleanup()
