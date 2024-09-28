import threading
# import winsound # uncomment for sound
import subprocess

import cv2
from cv2 import VideoWriter, VideoWriter_fourcc

from time import time, strftime, localtime

# Dropbox
import pathlib
from dropbox_handler import DropboxHandler

from dotenv.main import load_dotenv
import os

import requests
import json

class CameraSystem:
    def __init__(self) -> None:
        load_dotenv()
        self.DROPBOX_APP_KEY = os.environ['DROPBOX_APP_KEY']
        self.DROPBOX_APP_SECRET = os.environ['DROPBOX_APP_SECRET']
        self.DROPBOX_REFRESH_TOKEN = os.environ['DROPBOX_REFRESH_TOKEN']
        self.CAM_REQUEST_ENDPOINT = os.environ['CAM_REQUEST_ENDPOINT']
        self.ALARM_REPORT_ENDPOINT = os.environ['ALARM_REPORT_ENDPOINT']
        self.STATUS_REPORT_ENDPOINT = os.environ['STATUS_REPORT_ENDPOINT']
        self.EXTERNAL_DEVICE_NAME = os.environ['EXTERNAL_DEVICE_NAME']
        self.EXTERNAL_DEVICE_PATH = os.environ['EXTERNAL_DEVICE_PATH']

        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        self._, self.start_frame = self.cap.read()
        self.start_frame = cv2.cvtColor(self.start_frame, cv2.COLOR_BGR2GRAY)
        self.start_frame = cv2.GaussianBlur(self.start_frame, (21, 21), 0)

        self.alarm = False
        self.alarm_mode = False
        self.alarm_counter = 0

        self.recording = False
        self.video_length = 10000
        self.recording_start = 0
        self.file_name = 'recording.avi'
        self.video = cv2.VideoWriter(self.file_name, VideoWriter_fourcc(*'XVID'), 25.0, (640, 480))
        self.last_recording = ''
        self.img_file_name = ''
        self.upload_recording = False
        self.last_image_time = int(time()*1000)

        # Dropbox vars
        self.local_path = '.'
        self.dropbox_img_path = ''
        self.dropbox_video_path = ''
        self.unsent_images = []
        self.unsent_videos = []

        self.last_img_upload_time = int(time()*1000)
        self.last_vid_upload_time = int(time()*1000)
        self.last_status_report = int(time()*1000)

        # Check for recording requests
        self.last_request = int(time()*1000)

        # External Device
        self.external_image = ''
        self.external_video = ''
        self.external_status = ''
        self.external_request_delay = 0

        # Threading
        self.upload_img_thread = None
        self.upload_vid_thread = None
        self.check_request_thread = None
        self.report_alarm_thread = None
        self.beep_alarm_thread = None

    def dropbox_upload_img(self):
        dropbox_handler = DropboxHandler(self.DROPBOX_APP_KEY, self.DROPBOX_APP_SECRET, self.DROPBOX_REFRESH_TOKEN)

        if dropbox_handler:
            if len(self.unsent_images) > 0:
                print("UPLOADING ",len(self.unsent_images)," UNSENT IMAGES")
                for i in self.unsent_images:
                    local_file_path = pathlib.Path(self.local_path) / str(i)
                    dpx_path = '/MingSec/'+str(i)
                    dropbox_handler.upload_file(str(local_file_path), dpx_path)
                self.unsent_images.clear()

            local_file_path = pathlib.Path(self.local_path) / self.img_file_name
            dropbox_handler.upload_file(str(local_file_path), self.dropbox_img_path)
        else:
            local_file_path = pathlib.Path(self.local_path) / self.img_file_name
            self.unsent_images.append(local_file_path)
            print('Error uploading image to Dropbox:', local_file_path)

    def dropbox_upload_video(self):
        dropbox_handler = DropboxHandler(self.DROPBOX_APP_KEY, self.DROPBOX_APP_SECRET, self.DROPBOX_REFRESH_TOKEN)

        if dropbox_handler:
            if len(self.unsent_videos) > 0:
                print("UPLOADING ",len(self.unsent_videos)," UNSENT VIDEOS")
                for i in self.unsent_videos:
                    local_file_path = pathlib.Path(self.local_path) / str(i)
                    dpx_path = '/MingSec/'+str(i)
                    dropbox_handler.upload_file(str(local_file_path), dpx_path)

            local_file_path = pathlib.Path(self.local_path) / self.img_file_name
            dropbox_handler.upload_file(str(local_file_path), self.dropbox_video_path)
        else:
            local_file_path = pathlib.Path(self.local_path) / self.last_recording
            self.unsent_videos.append(local_file_path)
            print('Error uploading video to Dropbox:', local_file_path)

    def beep_alarm(self):
        for i in range(5):
            if not self.alarm_mode:
                break
            print("ALARM...",i)
            # winsound.Beep(2500, 1000) # uncomment for sound
        self.alarm = False

    def report_alarm(self):
        try:
            r = requests.post(self.ALARM_REPORT_ENDPOINT, json={'camera':'PC'})
            print("ALARM REPORT SENT", r.text)
        except Exception as e:
            print("UNABLE TO SEND ALARM REPORT... ", e)

    def report_status(self, camera, temperature):
        try:
            r = requests.post(self.STATUS_REPORT_ENDPOINT, json={'camera':camera, 'status':temperature})
            print("STATUS REPORT SENT", r.text)
        except Exception as e:
            print("UNABLE TO SEND STATUS REPORT... ", e)

    def check_requests(self):
        # print("THREADS: ", threading.active_count()) # for testing
        try:
            print("CHECKING FOR REQUESTS")

            if len(self.external_image) > 0:
                if self.external_request_delay < 3:
                    self.external_request_delay += 1
                elif self.external_request_delay == 3:
                    self.external_request_delay += 1
                    # Rename image
                    print("RENAMING IMAGE")
                    command = ["ssh", self.EXTERNAL_DEVICE_NAME, "cd", self.EXTERNAL_DEVICE_PATH+" && ", "mv", "ImageSSH.jpg "+self.external_image+" && ", "exit"]
                    subprocess.run(command)
                else:
                    self.external_request_delay = 0
                    # Transfer to local device
                    print("FETCHING EXT IMAGE")
                    command = ["scp", self.EXTERNAL_DEVICE_NAME+":"+self.EXTERNAL_DEVICE_PATH+"/"+self.external_image, "."]
                    subprocess.run(command)
                    self.unsent_images.append(self.external_image)
                    self.external_image = ''

            if len(self.external_video) > 0:
                if self.external_request_delay < 6:
                    self.external_request_delay += 1
                elif self.external_request_delay == 6:
                    self.external_request_delay += 1
                    # Rename video
                    print("RENAMING VIDEO")
                    command = ["ssh", self.EXTERNAL_DEVICE_NAME, "cd", self.EXTERNAL_DEVICE_PATH+" && ", "mv", "VideoSSH.avi "+self.external_video+" && ", "exit"]
                    subprocess.run(command)
                else:
                    self.external_request_delay = 0
                    # Transfer to local device
                    print("FETCHING EXT VIDEO")
                    command = ["scp", self.EXTERNAL_DEVICE_NAME+":"+self.EXTERNAL_DEVICE_PATH+"/"+self.external_video, "."]
                    subprocess.run(command)
                    self.unsent_videos.append(self.external_video)
                    self.external_video = ''

            req = requests.get(self.CAM_REQUEST_ENDPOINT)
            request_dict = json.loads(req.content)
            if len(request_dict)>0:
                request_data = request_dict[-1]
                print(request_data)

                if request_data['camera'].lower()=='pc' or request_data['camera'].lower()=='external':
                    if request_data['type'].lower()=='image':

                        if request_data['time']>self.last_img_upload_time:
                            self.last_img_upload_time = int(time()*1000)
                            if request_data['camera'].lower()=='external':
                                print("EXT IMAGE REQUESTED")
                                self.external_image = strftime("EXTERNAL_REQUESTED_%Y-%m-%d_%H-%M-%S", localtime())+'.jpg'
                                # Capture image on external device
                                command = ["ssh", self.EXTERNAL_DEVICE_NAME, "cd", self.EXTERNAL_DEVICE_PATH+" && ", 
                                        "source", "venv/bin/activate && ", "python3", "cap_image.py"+" && ", 
                                        "exit"]
                                subprocess.run(command)
                            else:
                                print("IMAGE REQUESTED")
                                self.img_file_name = strftime("PC_REQUESTED_%Y-%m-%d_%H-%M-%S", localtime())+'.jpg'
                                _, frame = self.cap.read()
                                cv2.imwrite(self.img_file_name, frame)
                                if len(self.img_file_name) > 0:
                                    self.dropbox_img_path = '/MingSec/'+self.img_file_name
                                    if self.upload_img_thread is None or not self.upload_img_thread.is_alive():
                                        self.upload_img_thread = threading.Thread(target=self.dropbox_upload_img, daemon=True)
                                        self.upload_img_thread.start()

                    if request_data['type'].lower()=='video':

                        if request_data['time']>self.last_vid_upload_time:
                            self.last_vid_upload_time = int(time()*1000)
                            if request_data['camera'].lower()=='external':
                                print("EXT VIDEO REQUESTED")
                                self.external_video = strftime("EXTERNAL_REQUESTED_%Y-%m-%d_%H-%M-%S", localtime())+'.avi'
                                # Capture video on external device
                                command = ["ssh", self.EXTERNAL_DEVICE_NAME, "cd", self.EXTERNAL_DEVICE_PATH+" && ", 
                                        "source", "venv/bin/activate && ", "python3", "cap_video.py"+" && ", 
                                        "exit"]
                                subprocess.run(command)
                            else:
                                self.last_vid_upload_time = int(time()*1000)
                                print("VIDEO REQUESTED")
                                self.file_name = strftime("PC_REQUESTED_%Y-%m-%d_%H-%M-%S", localtime())+'.avi'
                                self.last_recording = self.file_name
                                self.video = cv2.VideoWriter(self.file_name, VideoWriter_fourcc(*'XVID'), 25.0, (640, 480))
                                self.recording_start = int(time() * 1000)
                                self.recording = True

                    if request_data['type'].lower()=='status':

                        if request_data['time']>self.last_status_report:
                            self.last_status_report = int(time()*1000)
                            if request_data['camera'].lower()=='external':
                                print("EXT STATUS REQUESTED")
                                command = ["ssh", self.EXTERNAL_DEVICE_NAME, "cd", self.EXTERNAL_DEVICE_PATH+" && ", 
                                        "cat", "/sys/class/thermal/thermal_zone*/temp && ", 
                                        "exit"]
                                sub_output = subprocess.check_output(command, shell=False)
                                # ext_report = "EXT TEMP: " + ", ".join(sub_output.decode('utf-8'))
                                ext_report_raw = sub_output.decode('utf-8')

                                # Create a single string of temperatures
                                temperatures = ext_report_raw.splitlines()
                                # Clean and join the temperature values
                                ext_report = "EXT TEMP: " + ", ".join(temp.strip() for temp in temperatures if temp.strip())

                                print("****EXT STATUS****",ext_report)
                                print("****EXT STATUS LEN****",len(ext_report))
                                self.report_status("EXT", ext_report)
                            else:
                                print("STATUS REQUESTED")
                                self.report_status("PC", "OK")

        except Exception as e:
            print('Unable to connect to API: ' + str(e))

    def run(self):
        while True:
            _, frame = self.cap.read()

            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(frame,strftime("%H:%M:%S", localtime()),(10,30), font, 1,(0,0,255),2,cv2.LINE_AA)

            if self.alarm_mode:
                frame_bw = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
                frame_bw = cv2.GaussianBlur(frame_bw, (5, 5), 0)

                difference = cv2.absdiff(frame_bw, self.start_frame)
                threshold = cv2.threshold(difference, 25, 255, cv2.THRESH_BINARY)[1]
                self.start_frame = frame_bw

                if threshold.sum() > 300: # smaller is more sensitive
                    self.alarm_counter += 1
                else:
                    if self.alarm_counter > 0:
                        self.alarm_counter -= 1

                cv2.imshow("Cam", threshold)

            else:
                cv2.imshow("Cam", frame)

            # Check for requests
            if int(time()*1000) - self.last_request > 10000:
                self.last_request = int(time()*1000)
                if self.check_request_thread is None or not self.check_request_thread.is_alive():
                    self.check_request_thread = threading.Thread(target=self.check_requests, daemon=True)
                    self.check_request_thread.start()

            # Save and upload image every 10 minutes
            if int(time()*1000) - self.last_image_time > 600000:
                # Turn on alarm mode
                self.alarm_mode = True
                print("SAVE IMG")
                self.last_image_time = int(time()*1000)
                self.img_file_name = strftime("PC_%Y-%m-%d_%H-%M-%S", localtime())+'.jpg'
                cv2.imwrite(self.img_file_name, frame)
                if len(self.img_file_name) > 0:
                    self.dropbox_img_path = '/MingSec/'+self.img_file_name
                    if self.upload_img_thread is None or not self.upload_img_thread.is_alive():
                        self.upload_img_thread = threading.Thread(target=self.dropbox_upload_img, daemon=True)
                        self.upload_img_thread.start()
            
            if self.recording:
                self.video.write(frame)
                if int(time() * 1000) - self.recording_start > self.video_length:
                    print("stop recording")
                    self.video_length = 10000
                    self.recording_start = 0
                    self.recording = False
                    if len(self.last_recording) > 0:
                        # Release last recording
                        self.file_name = 'recording.avi'
                        self.video = cv2.VideoWriter(self.file_name, VideoWriter_fourcc(*'XVID'), 25.0, (640, 480))

                        self.dropbox_video_path = '/MingSec/'+self.last_recording
                        if self.upload_vid_thread is None or not self.upload_vid_thread.is_alive():
                            self.upload_vid_thread = threading.Thread(target=self.dropbox_upload_video, daemon=True)
                            self.upload_vid_thread.start()

            if self.alarm_counter > 20:
                if not self.alarm:
                    self.alarm = True
                    if self.recording_start == 0:
                        if self.report_alarm_thread is None or not self.report_alarm_thread.is_alive():
                            self.report_alarm_thread = threading.Thread(target=self.report_alarm, daemon=True)
                            self.report_alarm_thread.start()
                        # Alarm Image
                        self.img_file_name = strftime("PC_ALARM_%Y-%m-%d_%H-%M-%S", localtime())+'.jpg'
                        cv2.imwrite(self.img_file_name, frame)
                        if len(self.img_file_name) > 0:
                            self.dropbox_img_path = '/MingSec/'+self.img_file_name
                            if self.upload_img_thread is None or not self.upload_img_thread.is_alive():
                                self.upload_img_thread = threading.Thread(target=self.dropbox_upload_img, daemon=True)
                                self.upload_img_thread.start()

                        self.file_name = strftime("PC_ALARM_%Y-%m-%d_%H-%M-%S", localtime())+'.avi'
                        self.last_recording = self.file_name
                        self.video = cv2.VideoWriter(self.file_name, VideoWriter_fourcc(*'XVID'), 25.0, (640, 480))
                        self.recording = True
                    self.recording_start = int(time() * 1000)
                    if self.beep_alarm_thread is None or not self.beep_alarm_thread.is_alive():
                        self.beep_alarm_thread = threading.Thread(target=self.beep_alarm, daemon=True)
                        self.beep_alarm_thread.start()

            key_pressed = cv2.waitKey(30)
            if key_pressed == ord("t"):
                self.alarm_mode = not self.alarm_mode
                self.alarm_counter = 0

            if key_pressed == ord("q"):
                self.alarm_mode = False
                break
        self.shutdown()

    def shutdown(self):
        self.video.release()
        self.cap.release()
        cv2.destroyAllWindows()
        if self.upload_img_thread is not None:
            self.upload_img_thread.join()
        if self.upload_vid_thread is not None:
            self.upload_vid_thread.join()
        if self.check_request_thread is not None:
            self.check_request_thread.join()
        if self.report_alarm_thread is not None:
            self.report_alarm_thread.join()
        if self.beep_alarm_thread is not None:
            self.beep_alarm_thread.join()

if __name__ == "__main__":
    camera_system = CameraSystem()
    camera_system.run()