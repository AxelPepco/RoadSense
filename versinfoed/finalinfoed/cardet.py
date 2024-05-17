from roadfunc import *
from vehiclefunc import *
import math
import random
from scipy.spatial import distance


global car_position
global prev_pos
prev_pos = None
car_position = None
cap = cv2.VideoCapture("cars.mp4")


def avgCnt(frame,pos):
    x1,y1,x2,y2 = pos
    frame = frame[y1:y2,x1:x2]
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame = cv2.adaptiveThreshold(frame,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
 cv2.THRESH_BINARY,11,2)
    return frame

while cap.isOpened():
    _, frame = cap.read()
    frame_show = frame
    h,w,chan = frame.shape
    
    car_position = procesareVehicle(frame)
    for pos in car_position:
        x_min, y_min, x_max, y_max = pos
        frame_show = cv2.rectangle(frame_show, (x_min, y_min), (x_max, y_max), [255, 0, 0], 2)
    
    frame2 = avgCnt(frame,car_position[0])
    cv2.imshow("a", frame_show)
    cv2.imshow("b", frame2)
    print(len(car_position))
    cv2.waitKey(25)