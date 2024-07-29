import time
from FuzzyAlgs import fuzzy_functions
import socket

class Intersection:
    def __init__(self, name, coords, cams=None, orientations=None):
        self.ip = "127.0.0.1"
        self.port = 5009
        self.name = name
        self.coords = coords
        self.cams = cams if cams is not None else []
        self.orientations = orientations if orientations is not None else []

        self.managing = False
        self.camerasObjs = []

    def send_data(self, ip, port, data):
        # Trimite datele sistemului de gestionare a semafoarelor din simulator
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip, port))
        data_string = ','.join(data)
        client_socket.sendall(data_string.encode('utf-8'))
        client_socket.close()

    def add_cam(self, cam, orientation):
        # Adauga o camera si orientarea acesteia
        self.cams.append(cam)
        self.orientations.append(orientation)

    def __repr__(self):
        return f"Intersection(name={self.name}, coords={self.coords}, cams={self.cams}, orientations={self.orientations})"

    def start_managing(self):
        # Porneste gestionarea intersectiei
        self.managing = True

    def stop_managing(self):
        # Opreste gestionarea intersectiei
        self.managing = False

    def loadCameraObjs(self, cams):
        # Incarca camerele
        self.camerasObjs = cams

    def find_indices_of_word(self, array, word):
        indices = []
        for i, sub_array in enumerate(array):
            if word in sub_array:
                indices.append(i)
        return indices

    def calculate_cars(self, direction):
        # Calculeaza numarul de masini pe o anumita directie
        if direction not in self.orientations:
            return 0

        temp = self.orientations.index(direction)
        bands = self.camerasObjs[temp].cars
        directions = self.camerasObjs[temp].directions

        indices = self.find_indices_of_word(directions, 'Inainte')

        total_cars = sum(bands[index] for index in indices)

        return total_cars

    def assignColor(self, orientation, color):
        # Atribuie o culoare unei orientari
        temp = self.orientations.index(orientation)
        camera = self.camerasObjs[temp]
        camera.color = color

    def ManagingProcess(self):
        # Procesul de gestionare al intersectiei
        while self.managing:
            camNum = len(self.cams) - 1
            try:
                # Calculeaza numarul de masini pe fiecare directie
                north_cars = self.calculate_cars("North")
                east_cars = self.calculate_cars("East")
                south_cars = self.calculate_cars("South")
                west_cars = self.calculate_cars("West")

                print(f"North cars: {north_cars}")
                print(f"East cars: {east_cars}")
                print(f"South cars: {south_cars}")
                print(f"West cars: {west_cars}")

                # Foloseste algoritmul fuzzy pentru a determina semaforul si timpul
                inference = fuzzy_functions[camNum](north_cars, east_cars, south_cars, west_cars)
                print(inference)

                if inference[0] == "East/West":
                    # Seteaza culorile pentru directia Est/Vest
                    self.assignColor("East", "Green")
                    self.assignColor("West", "Green")
                    self.assignColor("North", "Red")
                    self.assignColor("South", "Red")
                    data = ["Green", "Green", "Red", "Red", inference[0], str(inference[1])]
                    self.send_data(self.ip, self.port, data)

                    time.sleep(inference[1] - 3)
                    self.assignColor("East", "Yellow")
                    self.assignColor("West", "Yellow")
                    self.assignColor("North", "Red")
                    self.assignColor("South", "Red")
                    data = ["Yellow", "Yellow", "Red", "Red", inference[0], str(inference[1])]
                    self.send_data(self.ip, self.port, data)

                    time.sleep(3)
                    self.assignColor("East", "Red")
                    self.assignColor("West", "Red")
                    self.assignColor("North", "Green")
                    self.assignColor("South", "Green")
                    data = ["Red", "Red", "Green", "Green", inference[0], str(inference[1])]
                    self.send_data(self.ip, self.port, data)

                    time.sleep(inference[1])

                elif inference[0] == "North/South":
                    # Seteaza culorile pentru directia Nord/Sud
                    self.assignColor("East", "Red")
                    self.assignColor("West", "Red")
                    self.assignColor("North", "Green")
                    self.assignColor("South", "Green")
                    data = ["Red", "Red", "Green", "Green", inference[0], str(inference[1])]
                    self.send_data(self.ip, self.port, data)

                    time.sleep(inference[1] - 3)
                    self.assignColor("East", "Red")
                    self.assignColor("West", "Red")
                    self.assignColor("North", "Yellow")
                    self.assignColor("South", "Yellow")
                    data = ["Red", "Red", "Yellow", "Yellow", inference[0], str(inference[1])]
                    self.send_data(self.ip, self.port, data)

                    time.sleep(3)
                    self.assignColor("East", "Green")
                    self.assignColor("West", "Green")
                    self.assignColor("North", "Red")
                    self.assignColor("South", "Red")
                    data = ["Green", "Green", "Red", "Red", inference[0], str(inference[1])]
                    self.send_data(self.ip, self.port, data)

                    time.sleep(inference[1])

            except Exception as e:
                print(f"Something happened when calculating cars: {e}")

            time.sleep(1)
