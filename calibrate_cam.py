# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))

time.sleep(0.1)

#i = [344, 272, 122]
i = [311, 332, 111]

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text
    image = frame.array

    img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cimg = img.copy()

    cimg = cv2.circle(cimg,(i[0],i[1]),i[2],(0,255,0),2)

    cv2.imshow('window', cimg)
    
    key = cv2.waitKey(1) & 0xFF

    if key != 255:
        # Adjust the radius
        if key == ord('p'):
            i[2] = i[2]+1
        if key == ord('o'):
            i[2] = i[2]-1

        # Adjust the y center
        if key == ord('h'):
            i[1] = i[1]+1
        if key == ord('j'):
            i[1] = i[1]-1

        # Adjust the x center
        if key == ord('k'):
            i[0] = i[0]+1
        if key == ord('l'):
            i[0] = i[0]-1

        if key == ord('q'):
            break

        print(i)

    rawCapture.truncate(0)
