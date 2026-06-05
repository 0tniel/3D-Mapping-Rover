import RPi.GPIO as GPIO
from pynput import keyboard
from time import sleep
import subprocess
import os
from datetime import datetime

# ==========================================
# MOTOR PINS
# ==========================================
IN1, IN2, ENA = 24, 23, 25
IN3, IN4, ENB = 17, 27, 18

SPEED = 60

# ==========================================
# VIDEO STORAGE
# ==========================================
VIDEO_DIR = "mapping_videos"
os.makedirs(VIDEO_DIR, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
video_file = os.path.join(VIDEO_DIR, f"room_scan_{timestamp}.mp4")

# ==========================================
# GPIO SETUP
# ==========================================
GPIO.setmode(GPIO.BCM)

GPIO.setup([IN1, IN2, IN3, IN4, ENA, ENB], GPIO.OUT)

GPIO.output([IN1, IN2, IN3, IN4], GPIO.LOW)

pwm_a = GPIO.PWM(ENA, 1000)
pwm_b = GPIO.PWM(ENB, 1000)

pwm_a.start(SPEED)
pwm_b.start(SPEED)

# ==========================================
# START LIVE PREVIEW + VIDEO RECORDING
# ==========================================
print("Starting Camera Preview...")
print("Recording Video for 3D Mapping...")

video_process = subprocess.Popen([
    "rpicam-vid",
    "-t", "0",
    "--width", "1280",
    "--height", "720",
    "--framerate", "30",
    "--codec", "mp4",
    "-o", video_file,
    "--preview", "0,0,1280,720"
])

sleep(2)

# ==========================================
# MOTOR FUNCTIONS
# ==========================================
def stop_motors():
    GPIO.output([IN1, IN2, IN3, IN4], GPIO.LOW)

def forward():
    GPIO.output([IN1, IN3], GPIO.HIGH)
    GPIO.output([IN2, IN4], GPIO.LOW)

def backward():
    GPIO.output([IN1, IN3], GPIO.LOW)
    GPIO.output([IN2, IN4], GPIO.HIGH)

def left():
    GPIO.output([IN1, IN4], GPIO.LOW)
    GPIO.output([IN2, IN3], GPIO.HIGH)

def right():
    GPIO.output([IN1, IN4], GPIO.HIGH)
    GPIO.output([IN2, IN3], GPIO.LOW)

# ==========================================
# KEYBOARD CONTROL
# ==========================================
def on_press(key):

    try:

        if key == keyboard.Key.up or (
            hasattr(key, 'char') and key.char == 'w'
        ):
            forward()

        elif key == keyboard.Key.down or (
            hasattr(key, 'char') and key.char == 's'
        ):
            backward()

        elif key == keyboard.Key.left or (
            hasattr(key, 'char') and key.char == 'a'
        ):
            left()

        elif key == keyboard.Key.right or (
            hasattr(key, 'char') and key.char == 'd'
        ):
            right()

    except:
        pass

def on_release(key):

    stop_motors()

    if key == keyboard.Key.esc:
        return False

# ==========================================
# INSTRUCTIONS
# ==========================================
print("\n===================================")
print("      3D MAPPING ROVER PILOT")
print("===================================")
print("W / UP       : Forward")
print("S / DOWN     : Backward")
print("A / LEFT     : Turn Left")
print("D / RIGHT    : Turn Right")
print("ESC          : Stop & Save Video")
print("===================================")
print(f"\nRecording To:\n{video_file}\n")

# ==========================================
# MAIN LOOP
# ==========================================
try:
    with keyboard.Listener(
        on_press=on_press,
        on_release=on_release
    ) as listener:
        listener.join()

finally:

    stop_motors()

    pwm_a.stop()
    pwm_b.stop()

    GPIO.cleanup()

    print("\nStopping Recording...")
    video_process.terminate()

    try:
        video_process.wait(timeout=3)
    except:
        pass

    print(f"\nVideo Saved:\n{video_file}")
    print("Ready for frame extraction and 3D reconstruction.")
