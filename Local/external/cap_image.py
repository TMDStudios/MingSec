# This file should be copied to the external device, be sure to turn on your webcam on the external device

import cv2
from time import strftime, localtime

IMG_FILE_NAME = 'ImageSSH.jpg'
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

FONT_SCALE = 1
FONT_THICKNESS = 2

def capture_image():
    cap = cv2.VideoCapture(0)
    try:
        if not cap.isOpened():
            raise RuntimeError("Could not open the camera.")

        ret, frame = cap.read()
        if not ret:
            raise RuntimeError("Frame not captured. Could not read frame from the camera.")

        if frame is not None and frame.size != 0:
            cv2.putText(frame, strftime("%H:%M:%S", localtime()), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, FONT_SCALE, (0, 0, 255), FONT_THICKNESS, cv2.LINE_AA)
            cv2.imwrite(IMG_FILE_NAME, frame)
            return f"Image saved as {IMG_FILE_NAME}"
        else:
            raise ValueError("Captured frame is empty, cannot save image.")
    finally:
        cap.release()

if __name__ == "__main__":
    try:
        capture_image()
    except Exception as e:
        raise RuntimeError(f"Error: {e}")