import time
import RPi.GPIO as GPIO
import pyaudio
import wave
import subprocess
import signal
import sys
import base64
import requests
import os


# 你的 API Key
API_KEY = "AIzaSyAJhhxErm-EmiwFuGx2zGrWrGG-NCZrh2Y"


# Google Speech-to-Text REST API URL
SPEECH_API_URL = f"https://speech.googleapis.com/v1/speech:recognize?key={API_KEY}"


# GPIO 初始化
GPIO.setmode(GPIO.BCM)


# 語音設定
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024


exit_flag = False


def signal_handler(signum, frame):
    global exit_flag
    print("收到終止信號，正在清理資源...")
    exit_flag = True


signal.signal(signal.SIGTERM, signal_handler)


def save_audio_to_file(frames, filename):
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    output_path = os.path.join(desktop, filename)
    with wave.open(output_path, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(pyaudio.PyAudio().get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
    print(f"錄音文件已保存至桌面: {output_path}")
    return output_path


def transcribe_audio(file_path):
    with open(file_path, "rb") as audio_file:
        audio_content = base64.b64encode(audio_file.read()).decode("utf-8")


    data = {
        "config": {
            "encoding": "LINEAR16",
            "sampleRateHertz": RATE,
            "languageCode": "zh-TW"
        },
        "audio": {
            "content": audio_content
        }
    }


    response = requests.post(SPEECH_API_URL, json=data)
    if response.status_code != 200:
        raise Exception(f"語音辨識API錯誤: {response.status_code} {response.text}")


    result = response.json()
    # 解析辨識結果
    if "results" in result and len(result["results"]) > 0:
        transcript = result["results"][0]["alternatives"][0]["transcript"]
        print(f"完整辨識結果: {transcript}")
        return transcript
    else:
        return ""


def main():
    global exit_flag
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    print("開始錄音，等待語音指令...")


    try:
        while not exit_flag:
            frames = []
            for _ in range(0, int(RATE / CHUNK * 3)):
                if exit_flag:
                    break
                data = stream.read(CHUNK)
                frames.append(data)


            if exit_flag:
                break


            audio_file = save_audio_to_file(frames, "debug_audio.wav")


            try:
                result = transcribe_audio(audio_file)
                print(f"辨識結果: {result}")


                if "鋁箔" in result.replace(" ", ""):
                    subprocess.run(["python3", "true90.py"])
                    time.sleep(5)
                    subprocess.run(["python3", "false90.py"])
                    
                elif "紙類"  in result.replace(" ", ""):
                    subprocess.run(["python3", "true180.py"])
                    time.sleep(5)
                    subprocess.run(["python3", "true180.py"])
                   
                elif "寶特瓶" in result.replace(" ", ""):
                    subprocess.run(["python3", "false90.py"])
                    time.sleep(5)
                    subprocess.run(["python3", "true90.py"])
                else:
                    print("未匹配任何關鍵詞")


            except Exception as e:
                print(f"語音辨識錯誤: {e}")


    except KeyboardInterrupt:
        print("手動停止程式")
    finally:
        print("清理資源...")
        stream.stop_stream()
        stream.close()
        audio.terminate()
        GPIO.cleanup()
        print("程式已結束")


if __name__ == "__main__":
    main()
