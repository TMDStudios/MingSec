import threading
# import winsound

import cv2
from cv2 import VideoWriter
from cv2 import VideoWriter_fourcc

from time import time, strftime, localtime

# Dropbox
import pathlib
import dropbox
from dropbox.exceptions import AuthError

from dotenv.main import load_dotenv
import os

load_dotenv()
APP_KEY = os.environ['APP_KEY']
APP_SECRET = os.environ['APP_SECRET']
REFRESH_TOKEN = os.environ['REFRESH_TOKEN']

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

_, start_frame = cap.read()
start_frame = cv2.cvtColor(start_frame, cv2.COLOR_BGR2GRAY)
start_frame = cv2.GaussianBlur(start_frame, (21, 21), 0)

alarm = False
alarm_mode = False
alarm_counter = 0

recording = False
recording_start = 0
file_name = 'recording.avi'
video = cv2.VideoWriter(file_name, VideoWriter_fourcc(*'XVID'), 25.0, (640, 480))
last_recording = ''
upload_recording = False
last_image_time = 0

def dropbox_connect():
    try:
        dbx = dropbox.Dropbox(
            app_key=APP_KEY,
            app_secret=APP_SECRET,
            oauth2_refresh_token=REFRESH_TOKEN
        )
    except AuthError as e:
        print('Error connecting to Dropbox with access token: ' + str(e))
    return dbx

def dropbox_upload_file(local_path, local_file, dropbox_file_path):
    try:
        dbx = dropbox_connect()

        local_file_path = pathlib.Path(local_path) / local_file

        with local_file_path.open("rb") as f:
            meta = dbx.files_upload(f.read(), dropbox_file_path, mode=dropbox.files.WriteMode("overwrite"))

            return meta
    except Exception as e:
        print('Error uploading file to Dropbox: ' + str(e))

def beep_alarm():
    global alarm
    for i in range(5):
        if not alarm_mode:
            break
        print("ALARM...",i)
        # winsound.Beep(2500, 1000)
    alarm = False

while True:
    _, frame = cap.read()

    if alarm_mode:
        frame_bw = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        frame_bw = cv2.GaussianBlur(frame_bw, (5, 5), 0)

        difference = cv2.absdiff(frame_bw, start_frame)
        threshold = cv2.threshold(difference, 25, 255, cv2.THRESH_BINARY)[1]
        start_frame = frame_bw

        if threshold.sum() > 300: # smaller is more sensitive
            alarm_counter += 1
        else:
            if alarm_counter > 0:
                alarm_counter -= 1

        cv2.imshow("Cam", threshold)

    else:
        cv2.imshow("Cam", frame)

    # Save and upload image every 10 minutes
    if int(time()*1000) - last_image_time > 600000:
        print("SAVE IMG")
        last_image_time = int(time()*1000)
        img_file_name = strftime("%Y-%m-%d_%H-%M-%S", localtime())+'.jpg'
        cv2.imwrite(img_file_name, frame)
        if len(img_file_name) > 0:
                dropbox_upload_file('.', img_file_name, '/MingSec/'+img_file_name)
    
    if recording:
        video.write(frame)
        if int(time() * 1000) - recording_start > 5000:
            print("stop recording")
            recording_start = 0
            recording = False
            if len(last_recording) > 0:
                dropbox_upload_file('.', last_recording, '/MingSec/'+last_recording)

    if alarm_counter > 20:
        if not alarm:
            alarm = True
            if recording_start == 0:
                file_name = strftime("%Y-%m-%d_%H-%M-%S", localtime())+'.avi'
                last_recording = file_name
                video = cv2.VideoWriter(file_name, VideoWriter_fourcc(*'XVID'), 25.0, (640, 480))
                recording = True
            recording_start = int(time() * 1000)
            threading.Thread(target=beep_alarm).start()

    key_pressed = cv2.waitKey(30)
    if key_pressed == ord("t"):
        alarm_mode = not alarm_mode
        alarm_counter = 0

    if key_pressed == ord("q"):
        alarm_mode = False
        break

video.release()
cap.release()
cv2.destroyAllWindows()