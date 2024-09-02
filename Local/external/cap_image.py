import cv2
from time import strftime, localtime

# This file should be copied to the external device, be sure to turn on your webcam on the external device

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Check if the camera opened successfully
if not cap.isOpened():
    print("Error: Could not open the camera.")
    exit()

img_file_name = 'ImageSSH.jpg'

ret, frame = cap.read()
if not ret:
    print("Error: Could not read frame from the camera.")
    cap.release()
    exit()

font = cv2.FONT_HERSHEY_SIMPLEX
cv2.putText(frame, strftime("%H:%M:%S", localtime()), (10,30), font, 1, (0,0,255), 2, cv2.LINE_AA)

# Check if the frame is empty before writing to a file
if frame is not None and frame.size != 0:
    cv2.imwrite(img_file_name, frame)
    print(f"Image saved as {img_file_name}")
else:
    print("Error: Captured frame is empty, cannot save image.")

cap.release()
cv2.destroyAllWindows()