import cv2
import numpy as np
from vehiclefunc import *
from setup import *
from carsonroad import *
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon



class CameraCam:
    def __init__(self, index):
        self.incoming = 0
        self.leaving = 0
        self.t =0
        self.index = index
        self.MAX_FRAMES = 1000
        self.N = 2
        self.THRESH = 30
        self.ASSIGN_VALUE = 255 #Value to assign the pixel if the threshold is met
        self.cap = cv2.VideoCapture(r"finalinfoed\cars.mp4")  # Use camera index 0 for the default camera

        self.i = 1
        self.roadPoints = []
        self.lanes = np.zeros_like(self.roadPoints)
        self.car_p = []
        self.directions = []

        self.processing = False






    def stop_processing(self):
        self.processing = False

    def quit(self):
        self.cap.release()
        self.processing = False

    # def secondcode(self):
    #     car = cv2.imread(r"finalinfoed\car.jpg")
    #     self.cap = cv2.VideoCapture(r"finalinfoed\cars.mp4")
    #     if self.start_processing:
    #         self.Processing()

    def SetUpCam(self):


        for t in range(MAX_FRAMES):
            ret, frame = self.cap.read()
            _,cnt,car_p = DetectCars(frame, t)
            print(cnt)
            if cnt  <20 and t>10:
                self.roadPoints,self.directions = SetUp(frame)
                break
            self.processing = True


    def Processing(self):
        MAX_FRAMES = 1000
        N = 2
        THRESH = 30
        ASSIGN_VALUE = 255 #Value to assign the pixel if the threshold is met

  
        # i = 1
        # self.roadPoints_array = np.array(self.roadPoints)

        # # Now create an array of zeros with the same shape as roadPoints_array
        # lanes = np.zeros_like(self.roadPoints_array)
        car_p = []


        # roadPoints = [[[205, 718], [738, 151], [1014, 154], [701, 718]], [[706, 719], [1025, 160], [1276, 148], [1252, 719]]]
        # directions = ["Inainte", "Invers"]
        cap = cv2.VideoCapture(r"finalinfoed\cars.mp4")
        for t in range(MAX_FRAMES):

            if  not self.processing:
                 break
            ret, frame = cap.read()
            frame ,cnt,car_p = DetectCars(frame, t)
            self.incoming = 0
            self.leaving = 0
            for car in car_p:
                x_min,y_min,x_max,y_max = car
                # carPoint = Point((x_max+x_min)/2,y_max )
                w,h = x_max-x_min,y_max-y_min
                carPol = Polygon([(x_min,y_min), (x_max,y_min),(x_max,y_max), (x_min, y_max)])
                percs = np.zeros_like(directions)
                for i in range(0,len(self.roadPoints)):
                    polygon = Polygon(self.roadPoints[i])
                    intersection_area = carPol.intersection(polygon).area

        # Calculate the percentage of intersection relative to the area of polygon1
                    percentage_intersection = (intersection_area / carPol.area) * 100
                    if len(percs) > 0:
                        percs[i] = percentage_intersection
                    
                    # if polygon.contains(carPoint):
                    #     if directions[i] == "Inainte":
                    #         leaving+=1
                    #     elif directions[i] == "Invers":
                    #         incoming+=1
                print(len(car_p))
                if len(percs) > 0:
                    print(percs)
                    max_index = np.argmax(percs)
                    if self.directions[max_index] == "Inainte":
                            self.leaving+=1
                    elif self.directions[max_index] == "Invers":
                            self.incoming+=1
                    frame = cv2.putText(frame,self.directions[max_index]+ ", " + percs[max_index],(x_min,y_min),cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),1)

            print(self.incoming,self.leaving)
            cv2.imshow("frame", frame)
            if cv2.waitKey(40) == ord('q'):
                 break
                #check overlap
                #add to lanes

            


            






