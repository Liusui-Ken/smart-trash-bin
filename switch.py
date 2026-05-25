import subprocess
import time
import RPi.GPIO as GPIO

BUTTON_PIN = 6

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

current_process = None
current_program = None

def start_program(script_name):
    global current_process, current_program
    current_process = subprocess.Popen(["python3", script_name])
    current_program = script_name
    print(f"已啟動 {script_name}")

def stop_program():
    global current_process
    if current_process is not None:
        print("停止程式...")
        current_process.terminate()
        current_process.wait()
        current_process = None

def switch_program():
    global current_program

    if current_program == "c.py":
        next_program = "classify.py"
    else:
        next_program = "c.py"

    # 先停止目前程式
    stop_program()
    time.sleep(0.5)  # 等待資源釋放

    # 啟動新程式
    start_program(next_program)

try:
    # 開機先啟動 c.py
    start_program("c.py")

    print("程式已啟動，按下按鈕切換程式...")

    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.LOW:
            switch_program()
            time.sleep(1)  # 防止按鈕彈跳

        time.sleep(0.1)

except KeyboardInterrupt:
    print("程式結束中...")

finally:
    stop_program()
    GPIO.cleanup()
