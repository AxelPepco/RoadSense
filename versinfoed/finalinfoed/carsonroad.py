from ultralytics import YOLO
import cv2
from roadfunc import *
from vehiclefunc import *
import math
import random
from scipy.spatial import distance

global car_position
frames=[]
MAX_FRAMES = 1000
N = 3
THRESH = 30
ASSIGN_VALUE = 255 #Value to assign the pixel if the threshold is met

# cap = cv2.VideoCapture("cars.mp4")  #Capture using Computer's Webcam
    
cap = cv2.VideoCapture("cars2.mp4")

def DetectCars(frame,t):
            
            car_position = []
            car_pos =[]
            cnt = 0
            #frame = cv2.resize(frame, (frame.shape[1]//2, frame.shape[0]//2))
            #Convert frame to grayscale
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY) 
            frame_gray =cv2.medianBlur(frame_gray, 3)
            #Append to list of frames
            frames.append(frame_gray)
            if t >= N:
                car_position = procesareVehicle(frame)
                car_pos = []

                diff = cv2.absdiff(frames[t-N], frames[t-1])

                threshold_method = cv2.THRESH_BINARY
                ret, motion_mask = cv2.threshold(diff, THRESH, ASSIGN_VALUE, threshold_method)

                cnt = 0

                for car in car_position:
                    x1,y1,x2,y2 = car
                    crop = motion_mask[y1:y2,x1:x2]
                    sum = np.count_nonzero(crop)

                    h,w = crop.shape
                    try:
                        perc = (sum/(h*w))*100
                    except:
                        perc = 0
                    if perc > 0.1:
                        cnt+=1
                        car_pos.append(car)
                    
                frame_show = frame
                # cv2.imshow('Motion Mask', motion_mask)
                for pos in car_pos:
                    x_min, y_min, x_max, y_max = pos  # Corrected order of coordinates
                    frame_show = cv2.rectangle(frame_show, (x_min, y_min), (x_max, y_max), [255, 0, 0], 2)


    
            return frame,cnt,car_pos