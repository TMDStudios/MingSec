import cv2
from cv2 import VideoWriter
from cv2 import VideoWriter_fourcc

from time import time

recording = False
recording_start = int(time()*1000)
file_name = 'VideoSSH.avi'
video = cv2.VideoWriter(file_name, VideoWriter_fourcc(*'XVID'), 25.0, (640, 480))

cam = cv2.VideoCapture(0)

while int(time()*1000) - recording_start < 10000:
    _, frame = cam.read()
   
    video.write(frame)

video.release()       
cam.release()
cv2.destroyAllWindows()