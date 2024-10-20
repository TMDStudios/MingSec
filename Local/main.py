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
import logging

class CameraSystem:
    # Load configuration from JSON file
    with open('config.json') as config_file:
        config = json.load(config_file)

    # Video settings
    FRAME_WIDTH = config['video_settings']['frame_width']
    FRAME_HEIGHT = config['video_settings']['frame_height']
    FRAME_RATE = config['video_settings']['frame_rate']
    FONT_SCALE = config['video_settings']['font_scale']
    FONT_THICKNESS = config['video_settings']['font_thickness']
    
    # Video lengths
    DEFAULT_VIDEO_LENGTH = config['video_lengths']['default_video_length']
    MAX_VIDEO_LENGTH = config['video_lengths']['max_video_length']

    # Intervals
    REQUEST_CHECK_INTERVAL = config['intervals']['request_check_interval']
    IMAGE_SAVE_INTERVAL = config['intervals']['image_save_interval']

    # Alarm settings
    ALARM_BEEP_COUNT = config['alarm_settings']['alarm_beep_count']
    ALARM_COUNTER_THRESHOLD = config['alarm_settings']['alarm_counter_threshold']

    # Camera settings
    GAUSSIAN_BLUR_KERNEL_SIZE_START = tuple(config['camera_settings']['gaussian_blur_kernel_size_start'])
    GAUSSIAN_BLUR_KERNEL_SIZE_DIFF = tuple(config['camera_settings']['gaussian_blur_kernel_size_diff'])
    GAUSSIAN_BLUR_KERNEL_SIZE = config['camera_settings']['gaussian_blur_kernel_size']
    CAMERA_INDEX = config['camera_settings']['camera_index']

    # Time conversion
    TIME_CONVERSION_MULTIPLIER = config['time_conversion']['time_conversion_multiplier']

    # Threshold values
    THRESHOLD_VALUE = config['threshold_values']['threshold_value']
    THRESHOLD_MAX = config['threshold_values']['threshold_max']
    THRESHOLD_SUM = config['threshold_values']['threshold_sum']

    # Beep settings
    BEEP_FREQUENCY = config['beep_settings']['beep_frequency']
    BEEP_DURATION = config['beep_settings']['beep_duration']

    # External request delays
    IMAGE_REQUEST_DELAY = config['external_request_delays']['image_request_delay']
    VIDEO_REQUEST_DELAY = config['external_request_delays']['video_request_delay']

    # Key delay
    WAIT_KEY_DELAY = config['key_delay']['wait_key_delay']

    # Log file
    LOG_FILE = config['log']['name']+strftime("%Y-%m-%d_%H-%M-%S", localtime())+'.txt'
    LOG_FILE_DROPBOX_PATH = config['log']['dropbox_path']+strftime("%Y-%m-%d_%H-%M-%S", localtime())+'.txt'

    def __init__(self) -> None:
        load_dotenv()
        self.DROPBOX_APP_KEY = os.environ['DROPBOX_APP_KEY']
        self.DROPBOX_APP_SECRET = os.environ['DROPBOX_APP_SECRET']
        self.DROPBOX_REFRESH_TOKEN = os.environ['DROPBOX_REFRESH_TOKEN']

        self.DROPBOX_APP_KEY_RW = os.environ['DROPBOX_APP_KEY_RW']
        self.DROPBOX_APP_SECRET_RW = os.environ['DROPBOX_APP_SECRET_RW']
        self.DROPBOX_REFRESH_TOKEN_RW = os.environ['DROPBOX_REFRESH_TOKEN_RW']

        self.MINGSEC_API_KEY = os.environ['MINGSEC_API_KEY']
        self.CAM_REQUEST_ENDPOINT = os.environ['CAM_REQUEST_ENDPOINT']
        self.ALARM_REPORT_ENDPOINT = os.environ['ALARM_REPORT_ENDPOINT']
        self.STATUS_REPORT_ENDPOINT = os.environ['STATUS_REPORT_ENDPOINT']

        self.EXTERNAL_DEVICE_NAME = os.environ['EXTERNAL_DEVICE_NAME']
        self.EXTERNAL_DEVICE_PATH = os.environ['EXTERNAL_DEVICE_PATH']

        self.headers = {'Authorization': 'Bearer '+self.MINGSEC_API_KEY}

        self.cap = cv2.VideoCapture(self.CAMERA_INDEX, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.FRAME_HEIGHT)

        self._, self.start_frame = self.cap.read()
        self.start_frame = cv2.cvtColor(self.start_frame, cv2.COLOR_BGR2GRAY)
        self.start_frame = cv2.GaussianBlur(self.start_frame, self.GAUSSIAN_BLUR_KERNEL_SIZE_START, self.GAUSSIAN_BLUR_KERNEL_SIZE)

        self.alarm = False
        self.alarm_mode = False
        self.alarm_counter = 0

        self.recording = False
        self.video_length = self.DEFAULT_VIDEO_LENGTH
        self.recording_start = 0
        self.file_name = 'recording.avi'
        self.video = cv2.VideoWriter(self.file_name, VideoWriter_fourcc(*'XVID'), self.FRAME_RATE, (self.FRAME_WIDTH, self.FRAME_HEIGHT))
        self.last_recording = ''
        self.img_file_name = ''
        self.upload_recording = False
        self.last_image_time = int(time()*self.TIME_CONVERSION_MULTIPLIER)

        # Logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        file_handler = logging.FileHandler(self.LOG_FILE)
        console_handler = logging.StreamHandler()

        file_handler.setLevel(logging.INFO)
        console_handler.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        self.unsent_log = False

        # Dropbox vars
        self.local_path = '.'
        self.dropbox_log_path = ''
        self.dropbox_img_path = ''
        self.dropbox_video_path = ''
        self.unsent_images = []
        self.unsent_videos = []
        self.dropbox_handler = DropboxHandler(self.DROPBOX_APP_KEY, self.DROPBOX_APP_SECRET, self.DROPBOX_REFRESH_TOKEN, self.logger)
        self.dropbox_log_handler = DropboxHandler(self.DROPBOX_APP_KEY_RW, self.DROPBOX_APP_SECRET_RW, self.DROPBOX_REFRESH_TOKEN_RW, self.logger, True)

        self.last_img_upload_time = int(time()*self.TIME_CONVERSION_MULTIPLIER)
        self.last_vid_upload_time = int(time()*self.TIME_CONVERSION_MULTIPLIER)
        self.last_status_report = int(time()*self.TIME_CONVERSION_MULTIPLIER)

        # Check for recording requests
        self.last_request = int(time()*self.TIME_CONVERSION_MULTIPLIER)

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

    def run_external_command(self, command, ext_status=False):
        if ext_status:
            try:
                result = subprocess.run(command, check=True, capture_output=True, text=True)
                return "OK"
            except (subprocess.CalledProcessError, RuntimeError) as e:
                return "UNABLE TO REACH EXTERNAL DEVICE"
        else:
            try:
                result = subprocess.run(command, check=True, capture_output=True, text=True)
                if "could not open the camera" in result.stdout.lower() or "camera index out of range" in result.stderr.lower():
                    self.external_image = ''
                    self.external_video = ''
                    return "EXTERNAL CAMERA ERROR"
                return "OK"
            except (subprocess.CalledProcessError, RuntimeError) as e:
                self.external_image = ''
                self.external_video = ''
                return "EXTERNAL CAMERA ERROR"
        
    def dropbox_upload_log(self):
        if self.dropbox_log_handler.connected:
            local_file_path = pathlib.Path(self.local_path) / self.LOG_FILE
            self.dropbox_log_handler.upload_file(str(local_file_path), self.LOG_FILE_DROPBOX_PATH)
        else:
            self.unsent_log = True
            self.logger.error(f'Error uploading log to Dropbox')

    def dropbox_upload_img(self):
        if self.dropbox_handler.connected:
            local_file_path = pathlib.Path(self.local_path) / self.img_file_name
            self.dropbox_handler.upload_file(str(local_file_path), self.dropbox_img_path)
        else:
            local_file_path = pathlib.Path(self.local_path) / self.img_file_name
            self.unsent_images.append(local_file_path)
            self.logger.error(f'Error uploading image to Dropbox: {local_file_path}')

    def dropbox_upload_video(self):
        if self.dropbox_handler.connected:
            local_file_path = pathlib.Path(self.local_path) / self.last_recording
            self.dropbox_handler.upload_file(str(local_file_path), self.dropbox_video_path)
            # if result!="OK":
            #     self.unsent_videos.append(local_file_path)
            #     self.logger.error(f'Error uploading video to Dropbox: {result}')
        else:
            local_file_path = pathlib.Path(self.local_path) / self.last_recording
            self.unsent_videos.append(local_file_path)
            self.logger.error(f'Error uploading video to Dropbox: {local_file_path}')

    def dropbox_upload_unsent(self, type):
        if self.dropbox_handler.connected and self.dropbox_log_handler.connected:
            if type=='image':
                self.logger.info(f"UPLOADING {len(self.unsent_images)} UNSENT IMAGES")
                for i in self.unsent_images:
                    local_file_path = pathlib.Path(self.local_path) / str(i)
                    dpx_path = '/MingSec/'+str(i)
                    self.dropbox_handler.upload_file(str(local_file_path), dpx_path)
                self.unsent_images.clear()
            elif type=='video':
                self.logger.info(f"UPLOADING {len(self.unsent_videos)} UNSENT VIDEOS")
                for i in self.unsent_videos:
                    local_file_path = pathlib.Path(self.local_path) / str(i)
                    dpx_path = '/MingSec/'+str(i)
                    self.dropbox_handler.upload_file(str(local_file_path), dpx_path)
                self.unsent_videos.clear()
            else:
                self.logger.info(f"UPLOADING LOG")
                local_file_path = pathlib.Path(self.local_path) / self.LOG_FILE
                self.dropbox_log_handler.upload_file(str(local_file_path), self.LOG_FILE_DROPBOX_PATH)
                self.unsent_log = False
        else:
            self.logger.warning("NO DROPBOX CONNECTION FOUND, ESTABLISHING NEW CONNECTION...")
            self.dropbox_handler.dbx = self.dropbox_handler.connect()
            self.dropbox_log_handler.dbx = self.dropbox_log_handler.connect()

    def beep_alarm(self):
        for i in range(self.ALARM_BEEP_COUNT):
            if not self.alarm_mode:
                break
            # winsound.Beep(self.BEEP_FREQUENCY, self.BEEP_DURATION) # uncomment for sound
        self.alarm = False

    def report_alarm(self):
        try:
            r = requests.post(self.ALARM_REPORT_ENDPOINT, headers=self.headers, json={'camera':'PC'})
            self.logger.info(f"ALARM REPORT SENT {r.text}")
        except Exception as e:
            self.logger.error(f"UNABLE TO SEND ALARM REPORT: {e}")

    def report_status(self, camera, temperature):
        try:
            r = requests.post(self.STATUS_REPORT_ENDPOINT, headers=self.headers, json={'camera':camera, 'status':temperature})
            self.logger.info(f"STATUS REPORT SENT {r.text}")
        except Exception as e:
            self.logger.error(f"UNABLE TO SEND STATUS REPORT: {e}")

    def check_requests(self):
        self.logger.debug(f"THREADS: {threading.active_count()}")
        if self.alarm:
            self.logger.warning(f"*** ALARM IS ACTIVE ***")

        # Upload unsent images, videos, and log
        if len(self.unsent_images) > 0:
            self.dropbox_upload_unsent('image')
        if len(self.unsent_videos) > 0:
            self.dropbox_upload_unsent('video')
        if self.unsent_log:
            self.dropbox_upload_unsent('log')

        try:
            self.logger.info("CHECKING FOR REQUESTS")

            if len(self.external_image) > 0:
                if self.external_request_delay < self.IMAGE_REQUEST_DELAY:
                    self.external_request_delay += 1
                elif self.external_request_delay == self.IMAGE_REQUEST_DELAY:
                    self.external_request_delay += 1
                    # Rename image
                    self.logger.info("RENAMING IMAGE")
                    command = ["ssh", self.EXTERNAL_DEVICE_NAME, "cd", self.EXTERNAL_DEVICE_PATH+" && ", "mv", "ImageSSH.jpg "+self.external_image+" && ", "exit"]
                    ssh_result = self.run_external_command(command)
                    if ssh_result == "OK":
                        self.logger.info("Renamed Image Successfully")
                    else:
                        self.logger.error(ssh_result)
                else:
                    self.external_request_delay = 0
                    # Transfer to local device
                    self.logger.info("FETCHING EXT IMAGE")
                    command = ["scp", self.EXTERNAL_DEVICE_NAME+":"+self.EXTERNAL_DEVICE_PATH+"/"+self.external_image, "."]
                    ssh_result = self.run_external_command(command)
                    if ssh_result == "OK":
                        self.logger.info("Fetched Image Successfully")
                        self.unsent_images.append(self.external_image)
                        self.external_image = ''
                    else:
                        self.logger.error(ssh_result)

            if len(self.external_video) > 0:
                if self.external_request_delay < self.VIDEO_REQUEST_DELAY:
                    self.external_request_delay += 1
                elif self.external_request_delay == self.VIDEO_REQUEST_DELAY:
                    self.external_request_delay += 1
                    # Rename video
                    self.logger.info("RENAMING VIDEO")
                    command = ["ssh", self.EXTERNAL_DEVICE_NAME, "cd", self.EXTERNAL_DEVICE_PATH+" && ", "mv", "VideoSSH.avi "+self.external_video+" && ", "exit"]
                    ssh_result = self.run_external_command(command)
                    if ssh_result == "OK":
                        self.logger.info("Renamed Video Successfully")
                    else:
                        self.external_video = ''
                        self.logger.error(ssh_result)
                else:
                    self.external_request_delay = 0
                    # Transfer to local device
                    self.logger.info("FETCHING EXT VIDEO")
                    command = ["scp", self.EXTERNAL_DEVICE_NAME+":"+self.EXTERNAL_DEVICE_PATH+"/"+self.external_video, "."]
                    ssh_result = self.run_external_command(command)
                    if ssh_result == "OK":
                        self.logger.info("Fetched Video Successfully")
                        self.unsent_videos.append(self.external_video)
                    else:
                        self.logger.error(ssh_result)
                    self.external_video = ''

            req = requests.get(self.CAM_REQUEST_ENDPOINT, headers=self.headers)
            json_array = []
            if req.status_code == 200:
                try:
                    json_array = json.loads(req.content)
                except json.JSONDecodeError:
                    self.logger.error("Invalid JSON received from the API.")
            else:
                self.logger.error(f"UNABLE TO REACH MingSec API. CODE: {req.status_code}")
            if len(json_array)>0:
                request_data = json_array[-1]
                self.logger.info(f"LAST REQUEST: {request_data}")

                if request_data['camera'].lower()=='pc' or request_data['camera'].lower()=='external':
                    if request_data['type'].lower()=='image':

                        if request_data['time']>self.last_img_upload_time:
                            self.last_img_upload_time = int(time()*self.TIME_CONVERSION_MULTIPLIER)
                            if request_data['camera'].lower()=='external':
                                self.logger.info("EXT IMAGE REQUESTED")
                                self.external_image = strftime("EXTERNAL_REQUESTED_%Y-%m-%d_%H-%M-%S", localtime())+'.jpg'
                                # Capture image on external device
                                command = ["ssh", self.EXTERNAL_DEVICE_NAME, f"cd {self.EXTERNAL_DEVICE_PATH} && source venv/bin/activate && python3 cap_image.py"]
                                ssh_result = self.run_external_command(command)
                                if ssh_result == "OK":
                                    self.logger.info("External Image Captured Successfully")
                                else:
                                    self.logger.error(ssh_result)
                            else:
                                if self.recording:
                                    self.logger.warning("IMAGE REQUEST IGNORED. CAMERA IS BUSY.")
                                else:
                                    self.logger.info("IMAGE REQUESTED")
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
                            try:
                                self.video_length = int(request_data['length'])*self.TIME_CONVERSION_MULTIPLIER
                                # Limit requested video length to 1 minute
                                if self.video_length > self.MAX_VIDEO_LENGTH:
                                    self.video_length = self.MAX_VIDEO_LENGTH
                            except:
                                self.logger.warning("Invalid video length. Using defauld of 10 seconds.")
                                
                            self.last_vid_upload_time = int(time()*self.TIME_CONVERSION_MULTIPLIER)
                            if request_data['camera'].lower()=='external':
                                self.logger.info("EXT VIDEO REQUESTED")
                                self.external_video = strftime("EXTERNAL_REQUESTED_%Y-%m-%d_%H-%M-%S", localtime())+'.avi'
                                # Capture video on external device
                                command = ["ssh", self.EXTERNAL_DEVICE_NAME, f"cd {self.EXTERNAL_DEVICE_PATH} && source venv/bin/activate && python3 cap_video.py --duration {self.video_length}"]
                                ssh_result = self.run_external_command(command)
                                if ssh_result == "OK":
                                    self.logger.info("External Video Captured Successfully")
                                else:
                                    self.logger.error(ssh_result)
                            else:
                                if self.recording:
                                    self.logger.warning("VIDEO REQUEST IGNORED. CAMERA IS BUSY.")
                                else:
                                    self.last_vid_upload_time = int(time()*self.TIME_CONVERSION_MULTIPLIER)
                                    self.logger.info("VIDEO REQUESTED")
                                    self.file_name = strftime("PC_REQUESTED_%Y-%m-%d_%H-%M-%S", localtime())+'.avi'
                                    self.last_recording = self.file_name
                                    self.video = cv2.VideoWriter(self.file_name, VideoWriter_fourcc(*'XVID'), self.FRAME_RATE, (self.FRAME_WIDTH, self.FRAME_HEIGHT))
                                    self.recording_start = int(time() * self.TIME_CONVERSION_MULTIPLIER)
                                    self.recording = True

                    if request_data['type'].lower()=='status':

                        if request_data['time']>self.last_status_report:
                            self.last_status_report = int(time()*self.TIME_CONVERSION_MULTIPLIER)
                            if request_data['camera'].lower()=='external':
                                self.logger.info("EXT STATUS REQUESTED")
                                command = ["ssh", self.EXTERNAL_DEVICE_NAME, "cd", self.EXTERNAL_DEVICE_PATH+" && ", 
                                        "cat", "/sys/class/thermal/thermal_zone*/temp && ", 
                                        "exit"]
                                ssh_result = self.run_external_command(command, True)
                                if ssh_result == "OK":
                                    sub_output = subprocess.check_output(command, shell=False)
                                    ext_report_raw = sub_output.decode('utf-8')
                                    temperatures = ext_report_raw.splitlines()
                                    ext_report = "EXT TEMP: " + ", ".join(temp.strip() for temp in temperatures if temp.strip())

                                    self.logger.debug(f"EXTERNAL REPORT SENT: {ext_report}")
                                    self.report_status("EXT", ext_report)
                                else:
                                    self.logger.error(ssh_result)
                            else:
                                self.logger.info("STATUS REQUESTED")
                                self.dropbox_upload_log()
                                self.report_status("PC", "OK")

        except Exception as e:
            self.logger.error(f'Unable to connect to API: {str(e)}')

    def display_frame(self, frame):
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, strftime("%H:%M:%S", localtime()), (10, 30), font, self.FONT_SCALE, (0, 0, 255), self.FONT_THICKNESS, cv2.LINE_AA)

        if self.alarm_mode:
            frame_bw = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            frame_bw = cv2.GaussianBlur(frame_bw, self.GAUSSIAN_BLUR_KERNEL_SIZE_DIFF, self.GAUSSIAN_BLUR_KERNEL_SIZE)
            difference = cv2.absdiff(frame_bw, self.start_frame)
            threshold = cv2.threshold(difference, self.THRESHOLD_VALUE, self.THRESHOLD_MAX, cv2.THRESH_BINARY)[1]
            self.start_frame = frame_bw

            if threshold.sum() > self.THRESHOLD_SUM: # smaller is more sensitive
                self.alarm_counter += 1
            else:
                if self.alarm_counter > 0:
                    self.alarm_counter -= 1
            cv2.imshow("Cam", threshold)
        else:
            cv2.imshow("Cam", frame)

    def check_for_requests(self):
        if int(time()*self.TIME_CONVERSION_MULTIPLIER) - self.last_request > self.REQUEST_CHECK_INTERVAL:
            self.last_request = int(time()*self.TIME_CONVERSION_MULTIPLIER)
            if self.check_request_thread is None or not self.check_request_thread.is_alive():
                self.check_request_thread = threading.Thread(target=self.check_requests, daemon=True)
                self.check_request_thread.start()

    def save_and_upload_image(self, frame):
        if int(time()*self.TIME_CONVERSION_MULTIPLIER) - self.last_image_time > self.IMAGE_SAVE_INTERVAL:
            self.alarm_mode = True
            self.logger.info("ALARM MODE ACTIVATED")
            self.logger.info("SAVE IMG")
            self.last_image_time = int(time()*self.TIME_CONVERSION_MULTIPLIER)
            self.img_file_name = strftime("PC_%Y-%m-%d_%H-%M-%S", localtime())+'.jpg'
            cv2.imwrite(self.img_file_name, frame)
            self.upload_image_to_dropbox()
    
    def upload_image_to_dropbox(self):
        if len(self.img_file_name) > 0:
            self.dropbox_img_path = '/MingSec/'+self.img_file_name
            if self.upload_img_thread is None or not self.upload_img_thread.is_alive():
                self.upload_img_thread = threading.Thread(target=self.dropbox_upload_img, daemon=True)
                self.upload_img_thread.start()

    def handle_video_recording(self, frame):
        if self.recording:
            self.video.write(frame)
            if int(time() * self.TIME_CONVERSION_MULTIPLIER) - self.recording_start > self.video_length:
                self.stop_recording()

    def stop_recording(self):
        self.logger.info("STOP RECORDING")
        self.recording_start = 0
        self.recording = False
        if len(self.last_recording) > 0:
            self.file_name = 'recording.avi' # Release last recording
            self.video = cv2.VideoWriter(self.file_name, VideoWriter_fourcc(*'XVID'), self.FRAME_RATE, (self.FRAME_WIDTH, self.FRAME_HEIGHT))
            self.unsent_videos.append(self.last_recording)
            self.last_recording = ''

    def alarm_check(self, frame):
        if self.alarm_counter > self.ALARM_COUNTER_THRESHOLD:
            if not self.alarm:
                self.alarm = True
                if self.recording_start == 0:
                    if self.report_alarm_thread is None or not self.report_alarm_thread.is_alive():
                        self.report_alarm_thread = threading.Thread(target=self.report_alarm, daemon=True)
                        self.report_alarm_thread.start()
                    # Alarm Image
                    self.img_file_name = strftime("PC_ALARM_%Y-%m-%d_%H-%M-%S", localtime())+'.jpg'
                    self.logger.warning(f"** ALARM TRIGGERED! RECORDING HAS STARTED. IMAGE HAS BEEN CAPTURED. **")
                    cv2.imwrite(self.img_file_name, frame)
                    if len(self.img_file_name) > 0:
                        self.dropbox_img_path = '/MingSec/'+self.img_file_name
                        if self.upload_img_thread is None or not self.upload_img_thread.is_alive():
                            self.upload_img_thread = threading.Thread(target=self.dropbox_upload_img, daemon=True)
                            self.upload_img_thread.start()

                    self.file_name = strftime("PC_ALARM_%Y-%m-%d_%H-%M-%S", localtime())+'.avi'
                    self.last_recording = self.file_name
                    self.video = cv2.VideoWriter(self.file_name, VideoWriter_fourcc(*'XVID'), self.FRAME_RATE, (self.FRAME_WIDTH, self.FRAME_HEIGHT))
                    self.recording = True
                    self.video_length = self.DEFAULT_VIDEO_LENGTH
                self.recording_start = int(time() * self.TIME_CONVERSION_MULTIPLIER)
                if self.beep_alarm_thread is None or not self.beep_alarm_thread.is_alive():
                    self.beep_alarm_thread = threading.Thread(target=self.beep_alarm, daemon=True)
                    self.beep_alarm_thread.start()

    def handle_key_input(self, key_pressed):
        if key_pressed == ord("t"):
            self.alarm_mode = not self.alarm_mode
            self.logger.info(f"ALARM MODE: {self.alarm_mode}")
            self.alarm_counter = 0
        if key_pressed == ord("q"):
            return "EXIT"

    def run(self):
        while True:
            _, frame = self.cap.read()

            self.display_frame(frame)
            self.check_for_requests()
            self.save_and_upload_image(frame)
            self.handle_video_recording(frame)
            self.alarm_check(frame)
            key_pressed = cv2.waitKey(self.WAIT_KEY_DELAY)
            key_input = self.handle_key_input(key_pressed)
            if key_input == "EXIT":
                break

        self.shutDown()

    def shutDown(self):
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
    try:
        camera_system.run()
    except KeyboardInterrupt:
        camera_system.logger.warning("Program exited with Ctrl+C")
    except Exception as e:
        camera_system.logger.error(f"An error occurred: {e}")
    finally:
        print("Exiting program...")