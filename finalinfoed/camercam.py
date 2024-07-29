import cv2
import numpy as np
from vehiclefunc import procesareVehicle
from setup import SetUp
from carsonroad import DetectCars
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import serial
import time

from loadFromUnity import*

# Clasa pentru initializarea si gestionarea camerelor, inclusiv procesarea imaginilor pentru detectarea si numararea masinilor
#Fiecare camera are propriul numar index distinct dat la declarare
class CameraCam:
    def __init__(self, index):
        # Initializeaza variabilele pentru procesarea imaginilor si comunicarea seriala
        self.incoming = 0
        self.leaving = 0
        self.t = 0
        self.index = index
        self.MAX_FRAMES = 1000
        self.N = 2
        self.THRESH = 30
        self.ASSIGN_VALUE = 255  
        self.cap = cv2.VideoCapture(r"finalinfoed\cars.mp4")  # Poate rula un video in loc camera live pentru testarea detectiei
        self.port = 5000 + index
        #Portul pentru camera virtuala si adreasa acesteia
        self.ip = "127.0.0.1"
        self.i = 1
        self.roadPoints = []
        self.lanes = np.zeros_like(self.roadPoints)
        self.car_p = []
        self.directions = []

        self.processing = False
        self.frames = []
        self.color = "Yellow"

    def stop_processing(self):
        # Opreste procesarea imaginilor
        self.processing = False

    def start_processing(self):
        # Incepe procesarea imaginilor
        self.processing = True

    def quit(self):
        # Elibereaza resursele si opreste procesarea
        self.cap.release()
        self.processing = False

    def SetUpCam(self, func):
        # Configureaza camera si stabileste punctele de drum si directiile
        server_address = "127.0.0.1"
        server_port = 5000 + self.index

        sock = connect_to_server(server_address, server_port)
        t = 0
        while True:
            frame = receive_frame(sock)
            _, cnt, self.car_p, self.frames = DetectCars(frame, t, self.frames, self.N, self.THRESH, self.ASSIGN_VALUE)

            if cnt < 20 and t > 10:
                self.roadPoints, self.directions = SetUp(frame, self.index)
                break
            self.processing = True
            t += 1
        func(True, self.roadPoints, self.directions)
        sock.close()

    def Processing(self):
        # Proceseaza imaginile pentru detectarea masinilor si comunica cu Arduino
        last_sent_time = time.time()
        try:
            arduino = serial.Serial(port=self.port, baudrate=115200, timeout=.1)
        except Exception as e:
            print(f"Error opening serial port: {e}")

        self.car_p = []
        print("Am inceput")
        server_address = "127.0.0.1"
        server_port = 5000 + self.index

        sock = connect_to_server(server_address, server_port)
        #Se asteapta conexiunea la camera virtuala

        t = 0
        while True:
            t += 1
            current_time = time.time()
            if not self.processing:
                cv2.destroyWindow(str(self.index))
                break
            if sock is not None:
                frame = receive_frame(sock)
                if len(frame) == 0:
                    continue

            frame, cnt, self.car_p, self.frames = DetectCars(frame, t, self.frames, self.N, self.THRESH, self.ASSIGN_VALUE)
            #frame = frameul actual,procesat pentru urmatorii pasi
            # cnt = numarul de masini detectate
            #self.car_p = lista pozitiilor masinilor detectate
            #frames = imagine care contine diferenta absoluta dintre cadrele video anterioare convertite in grayscale. Aceste cadre sunt folosite pentru a analiza miscarea intre cadre si pentru a detecta schimbari in scena
            self.incoming = 0
            self.leaving = 0

            self.cars = [0] * len(self.directions)

         
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

                if len(percs) > 0:
                    max_index = np.argmax(percs)
                    if max_index < len(self.cars):
                        self.cars[max_index] += 1
                    frame = cv2.putText(frame, "Banda " + str(max_index), (x_min, y_min), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 1)
            #Se verifica cat din masina se suprapune cu fiecare banda(aria suprapusa dintre cele doua poligoane) si se alege cea cu aria cea mai mare

            text = ""
            for i in range(len(self.directions)):
                text += "Banda " + str(i) + ", " + str(self.cars[i]) + "\n"
           
            cv2.imshow(str(self.index), frame)
            if cv2.waitKey(10) == ord('q'):
                cv2.destroyWindow(str(self.index))
                break

            if current_time - last_sent_time >= 1:
                try:
                    arduino.write(bytes(self.color + "\n", 'utf-8'))
                    print(self.color)
                    last_sent_time = current_time 
                except Exception as e:
                    pass
            #Se afiseaza masinile detectate, benzile si numarul de masini in miscare de pe fiecare si se trimite culoarea semaforului la placa arduino
