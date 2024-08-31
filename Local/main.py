import threading
# import winsound
import subprocess

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

import requests
import json

load_dotenv()
APP_KEY = os.environ['APP_KEY']
APP_SECRET = os.environ['APP_SECRET']
REFRESH_TOKEN = os.environ['REFRESH_TOKEN']
CAM_REQUEST_ENDPOINT = os.environ['CAM_REQUEST_ENDPOINT']
ALARM_REPORT_ENDPOINT = os.environ['ALARM_REPORT_ENDPOINT']
STATUS_REPORT_ENDPOINT = os.environ['STATUS_REPORT_ENDPOINT']
EXTERNAL_DEVICE_NAME = os.environ['EXTERNAL_DEVICE_NAME']
EXTERNAL_DEVICE_PATH = os.environ['EXTERNAL_DEVICE_PATH']

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
video_length = 10000
recording_start = 0
file_name = 'recording.avi'
video = cv2.VideoWriter(file_name, VideoWriter_fourcc(*'XVID'), 25.0, (640, 480))
last_recording = ''
img_file_name = ''
upload_recording = False
last_image_time = int(time()*1000)

# Dropbox vars
local_path = '.'
dropbox_img_path = ''
dropbox_video_path = ''
unsent_images = []
unsent_videos = []

last_img_upload_time = int(time()*1000)
last_vid_upload_time = int(time()*1000)
last_status_report = int(time()*1000)

# Check for recording requests
last_request = int(time()*1000)

# External Device
external_image = ''
external_video = ''
external_status = ''
external_request_delay = 0

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

def dropbox_upload_img():
    global unsent_images
    try:
        dbx = dropbox_connect()

        if len(unsent_images) > 0:
            print("UPLOADING ",len(unsent_images)," UNSENT IMAGES")
            for i in unsent_images:
                local_file_path = pathlib.Path(local_path) / str(i)
                with local_file_path.open("rb") as f:
                    dpx_path = '/MingSec/'+str(i)
                    meta = dbx.files_upload(f.read(), dpx_path, mode=dropbox.files.WriteMode("overwrite"))
                    print("IMAGE UPLOADED:",dropbox_img_path)
            unsent_images.clear()

        local_file_path = pathlib.Path(local_path) / img_file_name

        with local_file_path.open("rb") as f:
            meta = dbx.files_upload(f.read(), dropbox_img_path, mode=dropbox.files.WriteMode("overwrite"))
            print("IMAGE UPLOADED:",dropbox_img_path)
            return meta
    except Exception as e:
        local_file_path = pathlib.Path(local_path) / img_file_name
        unsent_images.append(local_file_path)
        print('Error uploading image to Dropbox: ' + str(e))

def dropbox_upload_video():
    global unsent_videos
    try:
        dbx = dropbox_connect()

        if len(unsent_videos) > 0:
            print("UPLOADING ",len(unsent_videos)," UNSENT VIDEOS")
            for i in unsent_videos:
                local_file_path = pathlib.Path(local_path) / str(i)
                with local_file_path.open("rb") as f:
                    dpx_path = '/MingSec/'+str(i)
                    meta = dbx.files_upload(f.read(), dpx_path, mode=dropbox.files.WriteMode("overwrite"))
                    print("VIDEO UPLOADED:",dropbox_video_path)
            unsent_videos.clear()

        local_file_path = pathlib.Path(local_path) / last_recording

        with local_file_path.open("rb") as f:
            meta = dbx.files_upload(f.read(), dropbox_video_path, mode=dropbox.files.WriteMode("overwrite"))
            print("VIDEO UPLOADED:",dropbox_video_path)
            return meta
    except Exception as e:
        local_file_path = pathlib.Path(local_path) / last_recording
        unsent_videos.append(local_file_path)
        print('Error uploading video to Dropbox: ' + str(e))

def beep_alarm():
    global alarm
    for i in range(5):
        if not alarm_mode:
            break
        print("ALARM...",i)
        # winsound.Beep(2500, 1000)
    alarm = False

def report_alarm():
    try:
        r = requests.post(ALARM_REPORT_ENDPOINT, json={'camera':'PC'})
        print("ALARM REPORT SENT", r.text)
    except Exception as e:
        print("UNABLE TO SEND ALARM REPORT... ", e)

def report_status(camera, temperature):
    try:
        r = requests.post(STATUS_REPORT_ENDPOINT, json={'camera':camera, 'status':temperature})
        print("STATUS REPORT SENT", r.text)
    except Exception as e:
        print("UNABLE TO SEND STATUS REPORT... ", e)  

def check_requests():
    # print("THREADS: ", threading.active_count())
    try:
        global last_img_upload_time, last_vid_upload_time, last_status_report, dropbox_img_path, img_file_name, last_recording, video, recording
        global recording_start, video_length, external_image, external_video, external_status, external_request_delay, unsent_images, unsent_videos
        print("CHECKING FOR REQUESTS")

        if len(external_image) > 0:
            if external_request_delay < 3:
                external_request_delay += 1
            elif external_request_delay == 3:
                external_request_delay += 1
                # Rename image
                print("RENAMING IMAGE")
                command = ["ssh", EXTERNAL_DEVICE_NAME, "cd", EXTERNAL_DEVICE_PATH+" && ", "mv", "ImageSSH.jpg "+external_image+" && ", "exit"]
                subprocess.run(command)
            else:
                external_request_delay = 0
                # Transfer to local device
                print("FETCHING EXT IMAGE")
                command = ["scp", EXTERNAL_DEVICE_NAME+":"+EXTERNAL_DEVICE_PATH+"/"+external_image, "."]
                subprocess.run(command)
                unsent_images.append(external_image)
                external_image = ''

        if len(external_video) > 0:
            if external_request_delay < 6:
                external_request_delay += 1
            elif external_request_delay == 6:
                external_request_delay += 1
                # Rename video
                print("RENAMING VIDEO")
                command = ["ssh", EXTERNAL_DEVICE_NAME, "cd", EXTERNAL_DEVICE_PATH+" && ", "mv", "VideoSSH.avi "+external_video+" && ", "exit"]
                subprocess.run(command)
            else:
                external_request_delay = 0
                # Transfer to local device
                print("FETCHING EXT VIDEO")
                command = ["scp", EXTERNAL_DEVICE_NAME+":"+EXTERNAL_DEVICE_PATH+"/"+external_video, "."]
                subprocess.run(command)
                unsent_videos.append(external_video)
                external_video = ''

        req = requests.get(CAM_REQUEST_ENDPOINT)
        request_dict = json.loads(req.content)
        if len(request_dict)>0:
            request_data = request_dict[-1]
            print(request_data)

            if request_data['camera'].lower()=='pc' or request_data['camera'].lower()=='external':
                if request_data['type'].lower()=='image':

                    if request_data['time']>last_img_upload_time:
                        last_img_upload_time = int(time()*1000)
                        if request_data['camera'].lower()=='external':
                            print("EXT IMAGE REQUESTED")
                            external_image = strftime("EXTERNAL_REQUESTED_%Y-%m-%d_%H-%M-%S", localtime())+'.jpg'
                            # Capture image on external device
                            command = ["ssh", EXTERNAL_DEVICE_NAME, "cd", EXTERNAL_DEVICE_PATH+" && ", 
                                       "source", "venv/bin/activate && ", "python3", "CapImage.py"+" && ", 
                                       "exit"]
                            subprocess.run(command)
                        else:
                            print("IMAGE REQUESTED")
                            img_file_name = strftime("PC_REQUESTED_%Y-%m-%d_%H-%M-%S", localtime())+'.jpg'
                            cv2.imwrite(img_file_name, frame)
                            if len(img_file_name) > 0:
                                dropbox_img_path = '/MingSec/'+img_file_name
                                threading.Thread(target=dropbox_upload_img).start()

                if request_data['type'].lower()=='video':

                    if request_data['time']>last_vid_upload_time:
                        last_vid_upload_time = int(time()*1000)
                        if request_data['camera'].lower()=='external':
                            print("EXT VIDEO REQUESTED")
                            external_video = strftime("EXTERNAL_REQUESTED_%Y-%m-%d_%H-%M-%S", localtime())+'.avi'
                            # Capture video on external device
                            command = ["ssh", EXTERNAL_DEVICE_NAME, "cd", EXTERNAL_DEVICE_PATH+" && ", 
                                       "source", "venv/bin/activate && ", "python3", "CapVideo.py"+" && ", 
                                       "exit"]
                            subprocess.run(command)
                        else:
                            last_vid_upload_time = int(time()*1000)
                            print("VIDEO REQUESTED")
                            file_name = strftime("PC_REQUESTED_%Y-%m-%d_%H-%M-%S", localtime())+'.avi'
                            last_recording = file_name
                            video = cv2.VideoWriter(file_name, VideoWriter_fourcc(*'XVID'), 25.0, (640, 480))
                            recording_start = int(time() * 1000)
                            recording = True

                if request_data['type'].lower()=='status':

                    if request_data['time']>last_status_report:
                        last_status_report = int(time()*1000)
                        if request_data['camera'].lower()=='external':
                            print("EXT STATUS REQUESTED")
                            command = ["ssh", EXTERNAL_DEVICE_NAME, "cd", EXTERNAL_DEVICE_PATH+" && ", 
                                       "cat", "/sys/class/thermal/thermal_zone*/temp && ", 
                                       "exit"]
                            sub_output = subprocess.check_output(command, shell=False)
                            ext_report = "EXT TEMP:", str(sub_output)
                            report_status("EXT", ext_report)
                        else:
                            print("STATUS REQUESTED")
                            report_status("PC", "OK")

    except Exception as e:
        print('Unable to connect to API: ' + str(e))

while True:
    _, frame = cap.read()

    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(frame,strftime("%H:%M:%S", localtime()),(10,30), font, 1,(0,0,255),2,cv2.LINE_AA)

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

    # Check for requests
    if int(time()*1000) - last_request > 10000:
        last_request = int(time()*1000)
        threading.Thread(target=check_requests).start()

    # Save and upload image every 10 minutes
    if int(time()*1000) - last_image_time > 600000:
        # Turn on alarm mode
        alarm_mode = True
        print("SAVE IMG")
        last_image_time = int(time()*1000)
        img_file_name = strftime("PC_%Y-%m-%d_%H-%M-%S", localtime())+'.jpg'
        cv2.imwrite(img_file_name, frame)
        if len(img_file_name) > 0:
            dropbox_img_path = '/MingSec/'+img_file_name
            threading.Thread(target=dropbox_upload_img).start()
    
    if recording:
        video.write(frame)
        if int(time() * 1000) - recording_start > video_length:
            print("stop recording")
            video_length = 10000
            recording_start = 0
            recording = False
            if len(last_recording) > 0:
                # Release last recording
                file_name = 'recording.avi'
                video = cv2.VideoWriter(file_name, VideoWriter_fourcc(*'XVID'), 25.0, (640, 480))

                dropbox_video_path = '/MingSec/'+last_recording
                threading.Thread(target=dropbox_upload_video).start()

    if alarm_counter > 20:
        if not alarm:
            alarm = True
            if recording_start == 0:
                threading.Thread(target=report_alarm).start()
                # Alarm Image
                img_file_name = strftime("PC_ALARM_%Y-%m-%d_%H-%M-%S", localtime())+'.jpg'
                cv2.imwrite(img_file_name, frame)
                if len(img_file_name) > 0:
                    dropbox_img_path = '/MingSec/'+img_file_name
                    threading.Thread(target=dropbox_upload_img).start()

                file_name = strftime("PC_ALARM_%Y-%m-%d_%H-%M-%S", localtime())+'.avi'
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