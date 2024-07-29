import cv2
from roadfunc import *
from vehiclefunc import procesareVehicle
import math
import random
from scipy.spatial import distance



def DetectCars(frame,t,frames,N, THRESH,ASSIGN_VALUE):
            

            
            car_position = []
            car_pos =[]
            cnt = 0

            frame_gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY) 
            frame_gray =cv2.medianBlur(frame_gray, 3)
            frames.append(frame_gray)
            #Se proceseaza imaginea sursa
            if t >= N:

                car_position = procesareVehicle(frame)
                #Se calculeaza pozitiile masinilor
                car_pos = []

                diff = cv2.absdiff(frames[t-N], frames[t-1])

                threshold_method = cv2.THRESH_BINARY
                ret, motion_mask = cv2.threshold(diff, THRESH, ASSIGN_VALUE, threshold_method)
                #Se face diferenta absoluta intre N imaginii si se proceseaza pentru a fii numarati pixelii din vectorul de miscare
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
                #Se determina daca masinile sunt stationare sau in miscare daca se afla pixelii diferiti de 0 in vectorul de miscare
                frame_show = frame

                for pos in car_pos:
                    x_min, y_min, x_max, y_max = pos  
                    frame_show = cv2.rectangle(frame_show, (x_min, y_min), (x_max, y_max), [255, 0, 0], 2)

                #Se incadreaza masinile in miscare in cadrul final pentru afisare
    
            return frame,cnt,car_pos,frames