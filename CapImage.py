import cv2

from time import strftime, localtime

# This file should be copied to the external device

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

img_file_name = 'ImageSSH.jpg'

_, frame = cap.read()
font = cv2.FONT_HERSHEY_SIMPLEX
cv2.putText(frame,strftime("%H:%M:%S", localtime()),(10,30), font, 1,(0,0,255),2,cv2.LINE_AA)

cv2.imwrite(img_file_name, frame)

cap.release()
cv2.destroyAllWindows()