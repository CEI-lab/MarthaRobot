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

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text
    image = frame.array

    img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cimg = img.copy()
    #circles = cv2.HoughCircles(img,cv2.HOUGH_GRADIENT,1.05,20,param1=50,param2=30,minRadius=120,maxRadius=140)
    #if not circles is None:
    #    circles = np.uint16(np.around(circles))
    #    for i in circles[0,:]:
    #        # draw the outer circle
    #        cv2.circle(cimg,(i[0],i[1]),i[2],(0,255,0),2)
    #        # draw the center of the circle
    #        cv2.circle(cimg,(i[0],i[1]),2,(0,0,255),3) 

    # circle for the top
    i = [344, 272, 122]
    cv2.circle(cimg,(i[0],i[1]),i[2],(0,255,0),2)

    # mask to only look at the top
    circle_mask = np.zeros_like(img).astype('uint8')
    circle_mask = cv2.circle(circle_mask,(i[0],i[1]),i[2],(255,255,255),cv2.FILLED)
    
    # apply threshold
    ret, thresh = cv2.threshold(img,60,255,cv2.THRESH_BINARY_INV)
    thresh = np.bitwise_and(thresh, circle_mask)

    # erode and dilate
    kernal = np.ones((10,10),np.uint8)
    thresh = cv2.erode(thresh,kernal, iterations=1)
    thresh = cv2.dilate(thresh,kernal, iterations=1)

    # find countours and get largest one
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    largest_con = []
    largest_area = 0
    for c in contours:
        area = cv2.contourArea(c)
        if area > largest_area:
            largest_con = [c]
            largest_area = area
        
    # draw the contour
    im_blobs = cv2.drawContours(img,largest_con, -1, (0,255,0), 3)
    center = None
    if largest_con:
        rect = cv2.minAreaRect(largest_con[0])
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        center = np.mean(box,axis=0)
        center = (int(center[0]), int(center[1]))
        im_blobs = cv2.circle(im_blobs, center, 3, (0,255,255),3)
        im_blobs = cv2.drawContours(im_blobs,[box],0,(0,255,255),2)

    # check where point is
    if center:
        if center[0] > i[0]:
            print('Right!')
        else:
            print('Left!')
    
    # show the frame
    #cv2.imshow("Frame", image)
    cv2.imshow("Frame", im_blobs)
    key = cv2.waitKey(1) & 0xFF
    
    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)
    
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break
