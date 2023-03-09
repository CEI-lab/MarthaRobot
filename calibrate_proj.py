import cv2
import numpy as np

cv2.namedWindow("window", cv2.WINDOW_FREERATIO)
cv2.setWindowProperty("window",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)

#i = [int(1706/2), int(959/2),int(122)]
i= [1160, 531, 418]

while True:

    img = np.zeros((959,1706))
    img = cv2.circle(img,(i[0],i[1]),i[2],(255,255,255),2)
    
    cv2.imshow('window', img)
    
    key = cv2.waitKey(0)

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

    
