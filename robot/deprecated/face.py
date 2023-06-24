import cv2
import numpy as np

#ret, sad = cv2.threshold(cv2.cvtColor(cv2.resize(cv2.imread('sad.png'),(100,100))  , cv2.COLOR_BGR2GRAY),127, 255, cv2.THRESH_BINARY)    
#ret, hap = cv2.threshold(cv2.cvtColor(cv2.resize(cv2.imread('happy.png'),(100,100)), cv2.COLOR_BGR2GRAY),127, 255, cv2.THRESH_BINARY) 
ret, sad = cv2.threshold(cv2.cvtColor(cv2.resize(cv2.imread('sad.png'),(100,100))  , cv2.COLOR_BGR2GRAY),127, 255, cv2.THRESH_BINARY)    
ret, hap = cv2.threshold(cv2.cvtColor(cv2.resize(cv2.imread('happy.png'),(100,100)), cv2.COLOR_BGR2GRAY),127, 255, cv2.THRESH_BINARY) 

cv2.imshow('hap',sad)

cv2.waitKey(0)

