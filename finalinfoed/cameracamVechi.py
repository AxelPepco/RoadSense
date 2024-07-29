import cv2
import numpy as np
from vehiclefunc import procesareVehicle
from setup import SetUp
from carsonroad import DetectCars
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import serial
import time


class CameraCam:
    def __init__(self, index):
        self.incoming = 0
        self.leaving = 0
        self.t = 0
        self.index = index
        self.MAX_FRAMES = 1000
        self.N = 2
        self.THRESH = 30
        self.ASSIGN_VALUE = 255  # Value to assign the pixel if the threshold is met
        self.cap = cv2.VideoCapture(r"finalinfoed\cars.mp4")  # Use camera index 0 for the default camera

        self.i = 1
        self.roadPoints = []
        self.lanes = np.zeros_like(self.roadPoints)
        self.car_p = []
        self.directions = []

        self.processing = False

        self.frames = []
        self.MAX_FRAMES = 1000
        self.N = 2
        self.THRESH = 30
        self.ASSIGN_VALUE = 255  # Value to assign the pixel if the threshold is met
        self.car_p = []
        self.cars = []

        self.port = None
        self.color = "Yellow"

    

    def stop_processing(self):
        self.processing = False

    def start_processing(self):
        self.processing = True

    def quit(self):
        self.cap.release()
        self.processing = False

    def SetUpCam(self,func):
        for t in range(self.MAX_FRAMES):
            ret, frame = self.cap.read()
            _, cnt, car_p, self.frames = DetectCars(frame, t, self.frames, self.N, self.THRESH, self.ASSIGN_VALUE)
           # print(cnt)
            if cnt < 20 and t > 10:
                self.roadPoints, self.directions = SetUp(frame, self.index)
                break
            self.processing = True
        func(True,self.roadPoints,self.directions)


    def ProcessingUnused(self):
        last_sent_time = time.time()
        try:
            arduino = serial.Serial(port=self.port, baudrate=115200, timeout=.1)
        except Exception as e:
            print(f"Error opening serial port: {e}")

        self.car_p = []
        cap = cv2.VideoCapture(r"finalinfoed\cars.mp4")

        for t in range(self.MAX_FRAMES):
            current_time = time.time()
            if not self.processing:
                
                cv2.destroyWindow(str(self.index))
                break
            ret, frame = cap.read()
            frame, cnt, self.car_p, self.frames = DetectCars(frame, t, self.frames, self.N, self.THRESH, self.ASSIGN_VALUE)
            self.incoming = 0
            self.leaving = 0

           # print(f"Number of directions: {len(self.directions)}")
            self.cars = [0] * len(self.directions)  # Initialize self.cars based on the number of directions

            for car in self.car_p:
                x_min, y_min, x_max, y_max = car
                w, h = x_max - x_min, y_max - y_min
                carPol = Polygon([(x_min, y_min), (x_max, y_min), (x_max, y_max), (x_min, y_max)])
                percs = np.zeros(len(self.directions))

                for i in range(len(self.roadPoints)):
                    polygon = Polygon(self.roadPoints[i])
                    intersection_area = carPol.intersection(polygon).area
                    percentage_intersection = (intersection_area / carPol.area) * 100
                    percs[i] = percentage_intersection

               # print(f"Car percentages: {percs}")

                if len(percs) > 0:
                    max_index = np.argmax(percs)
                    if max_index < len(self.cars):
                        self.cars[max_index] += 1
                    frame = cv2.putText(frame, "Banda " + str(max_index), (x_min, y_min), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 1)

            text = ""
            for i in range(len(self.directions)):
                text += "Banda " + str(i) + ", " + str(self.cars[i]) + "\n"
           # print(text)

           
            cv2.imshow(str(self.index), frame)
            if cv2.waitKey(10) == ord('q'):
                cv2.destroyWindow(str(self.index))
                break

            if current_time - last_sent_time >= 1:
                try:
                    arduino.write(bytes(self.color + "\n", 'utf-8'))
                    print(self.color)
                    last_sent_time = current_time  # Update the last sent time
                except Exception as e:
                    pass

        

# Ensure that the other parts of your code (e.g., DetectCars, SetUp, etc.) are correctly implemented and do not have bugs.

# Example usage:
# camera = CameraCam(0)
# camera.SetUpCam()
# camera.Processing()
