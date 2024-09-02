import cv2
from cv2 import VideoWriter, VideoWriter_fourcc
from time import time

# This file should be copied to the external device, be sure to turn on your webcam on the external device

# Initialize recording variables
recording_start = int(time()*1000)
file_name = 'VideoSSH.avi'
frame_width = 640
frame_height = 480
frame_rate = 25.0
recording_duration = 10000  # in milliseconds

# Try to open the video writer
try:
    fourcc = VideoWriter_fourcc(*'XVID')
    video = VideoWriter(file_name, fourcc, frame_rate, (frame_width, frame_height))
except Exception as e:
    print(f"Error initializing VideoWriter: {e}")
    exit(1)

# Try to open the webcam
cam = cv2.VideoCapture(0)
if not cam.isOpened():
    print("Error: Could not open webcam.")
    video.release()
    exit(1)

# Start recording
try:
    while int(time()*1000)-recording_start < recording_duration:
        ret, frame = cam.read()
        if not ret:
            print("Error: Could not read frame from webcam.")
            break
        video.write(frame)
except Exception as e:
    print(f"Error during recording: {e}")
finally:
    # Release resources
    video.release()
    cam.release()
    cv2.destroyAllWindows()
    print("Recording finished and resources released.")