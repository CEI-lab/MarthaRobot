# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np
import time

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))

time.sleep(0.1)

out = cv2.VideoWriter('choice.avi', cv2.VideoWriter_fourcc(
    'M', 'J', 'P', 'G'), 6.1, (640, 480))

cv2.namedWindow("window", cv2.WINDOW_FREERATIO)
cv2.setWindowProperty("window", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

size = 250
ret, sad = cv2.threshold(cv2.cvtColor(cv2.resize(cv2.imread(
    'sad.png'), (size, size)), cv2.COLOR_BGR2GRAY), 127, 255, cv2.THRESH_BINARY_INV)
ret, hap = cv2.threshold(cv2.cvtColor(cv2.resize(cv2.imread(
    'happy.png'), (size, size)), cv2.COLOR_BGR2GRAY), 127, 255, cv2.THRESH_BINARY_INV)

sad = cv2.rotate(sad, cv2.ROTATE_90_COUNTERCLOCKWISE)
hap = cv2.rotate(hap, cv2.ROTATE_90_COUNTERCLOCKWISE)

# circle for the top
cam_c = [357, 267, 122]
pro_c = [413, 678, 291]


def cam_to_proj(x, y):
    cam_c = [357, 267, 122]
    pro_c = [413, 678, 291]

    x_c = x - cam_c[0]
    y_c = y - cam_c[1]

    # get radius and angle
    r_c = np.sqrt(x_c**2 + y_c**2)
    theta_c = np.arctan2(y_c, x_c) + np.pi/2

    # scale radius and angle
    r_p = r_c*pro_c[2]/cam_c[2]
    theta_p = theta_c

    # convert back to cartesian for projector
    x_p = int(r_p*np.cos(theta_p) + pro_c[0])
    y_p = int(r_p*np.sin(theta_p) + pro_c[1])
    return x_p, y_p


def scale_contour(cnt, scale):
    M = cv2.moments(cnt)
    cx = int(M['m10']/M['m00'])
    cy = int(M['m01']/M['m00'])

    cnt_norm = cnt - [cx, cy]
    cnt_scaled = cnt_norm * scale
    cnt_scaled = cnt_scaled + [cx, cy]
    cnt_scaled = cnt_scaled.astype(np.int32)

    return cnt_scaled

#dot_img = np.zeros((959,1706))


start_time = time.time()

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text
    image = frame.array

    img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cimg = img.copy()

    # circle for the top
    cv2.circle(cimg, (cam_c[0], cam_c[1]), cam_c[2], (0, 255, 0), 2)

    # mask to only look at the top
    circle_mask = np.zeros_like(img).astype('uint8')
    circle_mask = cv2.circle(
        circle_mask, (cam_c[0], cam_c[1]), cam_c[2], (255, 255, 255), cv2.FILLED)

    # apply threshold
    ret, thresh = cv2.threshold(img, 60, 255, cv2.THRESH_BINARY_INV)
    thresh = np.bitwise_and(thresh, circle_mask)

    # create threshold for bright spots
    #ret, thresh_2 = cv2.threshold(img,150,255,cv2.THRESH_BINARY_INV)
    #thresh = np.bitwise_and(thresh, thresh_2)

    # erode and dilate
    kernal = np.ones((10, 10), np.uint8)
    thresh = cv2.erode(thresh, kernal, iterations=1)
    thresh = cv2.dilate(thresh, kernal, iterations=1)

    # find countours and get largest one
    contours, hierarchy = cv2.findContours(
        thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    largest_con = []
    largest_area = 0
    for c in contours:
        area = cv2.contourArea(c)
        if area > largest_area:
            largest_con = [c]
            largest_area = area

    # draw the contour
    im_blobs = cv2.drawContours(img, largest_con, -1, (0, 255, 0), 3)
    center = None
    if largest_con:

        rect = cv2.minAreaRect(largest_con[0])
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        center = np.mean(box, axis=0)
        center = (int(center[0]), int(center[1]))
        im_blobs = cv2.circle(im_blobs, center, 3, (0, 255, 255), 3)
        im_blobs = cv2.drawContours(im_blobs, [box], 0, (0, 255, 255), 2)

        x_p, y_p = cam_to_proj(center[0], center[1])

        #proj_con = np.zeros_like(box)
        # for i in range(box.shape[0]):
        #    proj_con[i,:] = list(cam_to_proj(box[i,0], box[i,1]))

        #proj_con = [scale_contour(proj_con, 1.3)]
        dot_img = np.zeros((959, 1706))
        #dot_img = cv2.circle(dot_img,(x_p,y_p),80,(255,255,255),cv2.FILLED)
        #dot_img = cv2.drawContours(dot_img,proj_con, -1, (255,255,255), 3)
        #dot_img = cv2.circle(dot_img,(x_p,y_p),100,(255,255,255),5)

        if center[0] < pro_c[0]:
            dot_img[pro_c[1]-int(size/2):pro_c[1]+int(size/2),
                    pro_c[0]-int(size/2):pro_c[0]+int(size/2)] = sad
        else:
            dot_img[pro_c[1]-int(size/2):pro_c[1]+int(size/2),
                    pro_c[0]-int(size/2):pro_c[0]+int(size/2)] = hap

    else:
        dot_img = np.zeros((959, 1706))
        dot_img[pro_c[1]-int(size):pro_c[1], pro_c[0] -
                int(size/2):pro_c[0]+int(size/2)] = sad
        dot_img[pro_c[1]:pro_c[1] +
                int(size), pro_c[0]-int(size/2):pro_c[0]+int(size/2)] = hap

    # show the frame
    out.write(cv2.cvtColor(im_blobs, cv2.COLOR_GRAY2RGB))
    #cv2.imshow("Frame", image)
    #cv2.imshow("Frame", im_blobs)
    cv2.imshow('window', dot_img)
    key = cv2.waitKey(1) & 0xFF

    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break

    fps = 1/(time.time()-start_time)
    start_time = time.time()
    # print(fps)
