# This file should be copied to the external device, be sure to turn on your webcam on the external device

import cv2
from cv2 import VideoWriter, VideoWriter_fourcc
from time import time
import argparse

FILE_NAME = 'VideoSSH.avi'
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FRAME_RATE = 25.0

ERROR_CAMERA_OPEN = "Could not open camera."
ERROR_FRAME_READ = "Could not read frame from camera."
ERROR_RECORDING = "Error during recording."

def initialize_video_writer():
    fourcc = VideoWriter_fourcc(*'XVID')
    return VideoWriter(FILE_NAME, fourcc, FRAME_RATE, (FRAME_WIDTH, FRAME_HEIGHT))

def capture_video(recording_duration):
    video = initialize_video_writer()
    cam = cv2.VideoCapture(0)

    if not cam.isOpened():
        video.release()
        raise RuntimeError(ERROR_CAMERA_OPEN)

    recording_start = int(time() * 1000)
    print("Recording started.")

    try:
        while int(time() * 1000) - recording_start < recording_duration:
            ret, frame = cam.read()
            if not ret:
                raise RuntimeError(ERROR_FRAME_READ)
            video.write(frame)
    except Exception as e:
        raise RuntimeError(f"{ERROR_RECORDING}: {e}")
    finally:
        video.release()
        cam.release()
        cv2.destroyAllWindows()
        print("Recording finished and resources released.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Capture video via SSH.')
    parser.add_argument('--duration', type=int, default=10000, 
                        help='Recording duration in milliseconds (default: 10000)')

    args = parser.parse_args()

    try:
        capture_video(args.duration)
    except Exception as e:
        raise RuntimeError(f"Error: {e}")