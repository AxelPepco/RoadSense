
Link Descarcare Simulator(Proiect Unity)
https://drive.google.com/drive/folders/1XRj5mdIKThYY4HETGjLoO5fDUN-wmphK

Documentație Proiect RoadSense 

Prezentare Generală 

RoadSense este o aplicație bazată pe Python, concepută pentru a monitoriza, analiza și gestiona traficul utilizând fluxuri video de la camere. Aplicația permite utilizatorilor să seteze camere în diferite locații, să marcheze zone de interes pe o hartă și să urmărească mișcările vehiculelor. Principalele componente ale proiectului includ elemente de GUI create cu Tkinter, procesarea video folosind OpenCV, analiza spațială folosind Shapely și utilizarea modelelor OpenVINO pentru detectarea vehiculelor. 


RoadSense este o aplicație concepută pentru a monitoriza, analiza și gestiona traficul. Aplicația permite utilizatorilor să seteze camere în diferite locații, să marcheze zone de interes pe o hartă, iar aplicația va controla fluxul traficului folosind logica Fuzzy și computer vision.


Principalele componente ale proiectului includ elemente de GUI create cu Tkinter, procesarea video folosind OpenCV, analiza spațială folosind Shapely și utilizarea modelelor OpenVINO pentru detectarea vehiculelor. De asemenea folosim Concurrent Futures pentru optimizare (rularea proceselor în paralel).
 
Funcționalitățile aplicației: 
Detecția vehiculelor: identifică și localizează vehiculele într-o imagine. 
Segmentarea drumului: segmentează drumul dintr-o imagine, evidențiind zona de drum și alte elemente relevante. 
Interfață grafică simplă pentru utilizator 
Integrarea hărților 
Gestionarea Intersecțiilor și a drumurilor folosind algoritmul fuzzy
Compatibilitatea cu semafoare reale 


De ce OpenVINO 
OpenVINO este un toolkit optimizat pentru a rula și optimiza modele de deep learning pe procesoare Intel și alte hardware-uri compatibile. Este foarte eficient pentru aplicațiile care necesită inferență rapidă și resurse limitate. De asemenea, oferă suport pentru o varietate de modele pre-antrenate și permite o integrare ușoară cu alte biblioteci și framework-uri folosite în Python. 
def procesareVehicle(image_de):
    # Redimensionează imaginea
    resized_image_de = cv2.resize(image_de, (width_de, height_de))
    input_image_de = np.expand_dims(resized_image_de.transpose(2, 0, 1), 0)
    
    # Detectează mașinile din imagine cu ajutorul modelului încărcat
    boxes = compiled_model_de([input_image_de])[output_keys_de]
    boxes = np.squeeze(boxes, (0, 1))
    boxes = boxes[~np.all(boxes == 0, axis=1)]





De ce concurrent.futures 
Biblioteca concurrent.futures permite gestionarea execuției în paralel a funcțiilor, optimizând astfel codul. Aceasta este esențială pentru procesarea simultană a imaginilor, asigurând că, în cazul unei erori, celelalte camere nu va fi afectate. De asemenea, această abordare previne procesarea treptate a camerelor, care ar putea duce la întârzieri semnificative între cadre.s



 
 
 
De ce Tkinter, tkintermaps 
Tkinter este o bibliotecă standard pentru crearea interfețelor grafice în Python. Este ușor de utilizat și permite crearea rapidă a interfețelor grafice simple. 
tkintermapview permite integrarea și vizualizarea hărților(de la o mulțime de provideri Ex Google Maps, OpenStreet,Tile etc) interactive în aplicațiile GUI. Este util pentru aplicațiile care necesită funcționalități de localizare și navigație, cum ar fi monitorizarea vehiculelor sau vizualizarea rutelor. 

 
De ce algoritmul Fuzzy:
 Acest sistem se adaptează dinamic la condițiile de trafic și la nevoile vehiculelor care tranzitează intersecția. Folosind logica fuzzy, putem lua în considerare o gamă largă de variabile, cum ar fi densitatea traficului, viteza vehiculelor și timpul de așteptare, pentru a determina momentul optim pentru schimbarea semafoarelor și pentru a asigura un flux eficient și sigur al traficului. Algoritmul fuzzy ne permite să luăm decizii în timp real, luând în considerare interacțiunea complexă dintre aceste variabile și ajustându-ne strategiile în funcție de schimbările din mediu. Astfel, putem optimiza timpul de așteptare al vehiculelor, reducând congestionarea și îmbunătățind în general mobilitatea în zona respectivă.


Componente Principale FUZZY
1. Clasa Intersection
Clasa Intersection este componenta centrală a sistemului. Aceasta gestionează camerele de supraveghere, colectează datele de trafic și controlează semafoarele pe baza algoritmului fuzzy.
class Intersection:
    def __init__(self, name, coords, cams=None, orientations=None):
        self.ip = "192.168.0.107"
        self.port = 5009
        self.name = name
        self.coords = coords
        self.cams = cams if cams is not None else []
        self.orientations = orientations if orientations is not None else []


        self.managing = False
        self.camerasObjs = []




name: Numele intersecției.
coords: Coordonatele geografice ale intersecției.
cams și orientations: Listele de camere și orientările acestora.






Metoda send_data
Aceasta metodă trimite date către sistemul de gestionare a semafoarelor.
def send_data(self, ip, port, data):
        # Trimite datele sistemului de gestionare a semafoarelor din simulator
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip, port))
        data_string = ','.join(data)
        client_socket.sendall(data_string.encode('utf-8'))
        client_socket.close()




Metoda calculate_cars
Calculează numărul de mașini pe o anumită direcție, utilizând datele de la camere.
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






2. Metoda ManagingProcess
Aceasta este metoda principală care gestionează traficul în intersecție. Utilizează logica fuzzy pentru a determina cum să schimbe culorile semafoarelor în funcție de densitatea traficului.
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








Funcții Speciale:
Detecție de Vehicule în mișcare: Camerele vor detecta doar imaginile in miscare (programul face o diferenta dintre valorile ultimelor N cadre, și determina dacă exista vreo diferenta între acestea, din care rezultă că obiectul s a mișcat)
Management inteligent al intersectiei utilizand logica Fuzzy:
Folosim logica fuzzy în proiect pentru a gestiona semafoarele într-un mod adaptativ, luând în considerare variabilele precum volumul traficului și timpul de așteptare pentru a controla fluxul de vehicule în intersecție.


Cod Simplu: Codul este foarte simplificat si impartit în trei parti: Interfata, Detectie, Gestionare Trafic
Fiecare sunt scrise ca functii si pot fii apelate individual pentru testare
Camerele funcționează pe baza unor instanțe ale clasei Camera, astfel putem chema cate camera distincte avem nevoie, ce ruleaza singure pe cate un thread. Fiecare au cate 4 funcții : start_processing(), stop_processing(), SetUp() si Processing()
Am redus codul pentru Detecție de la 640 linii la doar 5 linii:
from camercam import *
camera = CameraCam(0)
camera.SetUpCam()
camera.processing = True
camera.Processing()
 
Compatibilitate cu Semafoare Reale: Folosind un microprocesor(Arduino, WeMos, Raspberry etc), programul poate trimite comenzi prin Serial pentru a porni sau opri luminile
Harta Online și Offline: În cazul unei conexiuni la internet, programul va folosi o harta actuala de la serverul selectat, în caz contrar, va folosi o harta offline. Inginerul ce instalează semaforul își poate salva coordonatele exacte și le poate introduce in program pentru o poziționare cat mai precisa
Memorie Locala: Programul va salva local toate semafoarele adaugate ce vor fi reținute la următoarea pornire
Set-Up Camere:
Click dreapta pe harta în locul în care vrei sa plasezi un semafor, sau introdu coordonatele exacte în panoul din dreapta
Introdu un nume pentru Camera si COM port-ul microprocesorului conectat
În panoul din stanga, apăsa pe CamStatus pentru a gestiona Camerele create
Conectează firele astfel

(Schimbă pinii utilizați după preferință sau în funcție de placa de dezvoltare folosită)
Clasa CameraCam
Clasa CameraCam inițializează variabilele pentru procesarea imaginilor și configurarea camerei. Fiecare instanță a clasei CameraCam reprezintă o cameră distinctă ce rulează pe propriul thread in paralel faţă de celelalte.
class CameraCam:
    def __init__(self, index):
        self.incoming = 0
        self.leaving = 0
        self.t = 0
        self.index = index
        self.MAX_FRAMES = 1000
        self.N = 2
        self.THRESH = 30
        self.ASSIGN_VALUE = 255  
        self.cap = cv2.VideoCapture(r"finalinfoed\cars.mp4")  # Video de test
        self.port = 5000 + index
        self.ip = "192.168.0.107"
        self.i = 1
        self.roadPoints = []
        self.lanes = np.zeros_like(self.roadPoints)
        self.car_p = []
        self.directions = []
        self.processing = False
        self.frames = []
        self.color = "Yellow"



3. Funcţiile Clasei CameraCam
Funcţia stop_processing
Oprește procesarea imaginilor.


def stop_processing(self):
    self.processing = False



Funcţia start_processing
Începe procesarea imaginilor.


def start_processing(self):
    self.processing = True



Funcţia quit
Eliberează resursele și oprește procesarea.
def quit(self):
    self.cap.release()
    self.processing = False



Funcţia SetUpCam
Configurează camera și stabilește punctele de drum și direcțiile vehiculelor.


def SetUpCam(self, func):
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



Funcţia Processing
Procesează imaginile pentru detectarea vehiculelor și comunică cu un dispozitiv Arduino.
def Processing(self):
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

        self.incoming = 0
        self.leaving = 0
        self.cars = [0] * len(self.directions)

        for car in self.car_p:
            x_min, y_min, x_max, y_max = car
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



Utilizare Practică
Clasa CameraCam poate fi utilizată pentru a inițializa și gestiona camerele de supraveghere, a procesa imaginile pentru detectarea vehiculelor și a comunica cu un dispozitiv Arduino pentru controlul semafoarelor.
Exemplu de Utilizare
# Crearea instanței camerei
camera = CameraCam(index=0)

# Configurarea camerei
camera.SetUpCam(lambda success, roadPoints, directions: print("Setup complete", success))
# Începerea procesării imaginilor
camera.start_processing()
camera.Processing()





Modulul DetectCars

Funcția DetectCars procesează un cadru video pentru a detecta vehiculele prin conversia imaginii în gri, aplicarea unui blur median și calcularea diferenței absolute între N cadre. Aceasta identifică vehiculele pe baza diferenței de pixeli și le încadrează în imaginea finală pentru afișare. Funcția returnează cadrul procesat, numărul de vehicule detectate și pozițiile acestora.

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





Modulul SelectPoints
Funcția SelectPoints permite utilizatorului să configureze benzi de drum prin selectarea punctelor pe o imagine afișată. Punctele selectate sunt utilizate pentru a desena poligoane reprezentând drumuri. Utilizatorul poate termina configurarea unei benzi sau poate continua să adauge puncte. La apăsarea tastelor, configurarea se finalizează și informațiile despre drumuri și direcții sunt returnate.


from tkinter import *
from tkinter import ttk
from roadfunc import procesareRoad
from vehiclefunc import procesareVehicle
from PIL import Image, ImageTk
from functools import partial
import numpy as np


import cv2


def SelectPoints(testimage, indexCam):
    coords = []
    roads = []
    directions = []


    def finishRoad(coords, roads):
        if len(coords) > 2:
            polygon = []
            for point in coords:
                polygon.append(point)  
            roads.append(polygon)
            coords.clear()
        return coords, roads


    def drawPolygons(image, roads):
        if roads:
            for road in roads:
                pts = np.array(road, np.int32)  
                pts = pts.reshape((-1, 1, 2))    
                cv2.fillPoly(image, [pts], color=(0, 255, 0, 128))  
        return image


    def drawImage(img, coords):
        if len(coords) > 1:
            for i in range(1, len(coords)):
                prevx, prevy = coords[i-1]
                x, y = coords[i]
                img = cv2.circle(img, (x, y), 5, (0, 0, 255), -1)
                img = cv2.line(img, (prevx, prevy), (x, y), (0, 0, 255), 5)
        elif len(coords) == 1:
            x, y = coords[0]
            img = cv2.circle(img, (x, y), 5, (0, 0, 255), -1)
        return img


    def click_event(event, x, y, flags, params, org_img, coords):
        if event == cv2.EVENT_LBUTTONDOWN:
            coords.append([x, y])
            print(coords)
            image = org_img.copy()  
            image = drawPolygons(image, roads)
            image = drawImage(image, coords)


        if event == cv2.EVENT_RBUTTONDOWN:
            if coords:
                coords.pop()
                print(coords)
                image = org_img.copy()
                image = drawImage(image, coords)
             
            else:
                if roads:
                    roads.pop()
                    directions.pop()
                    if roads:
                        coords = roads[-1]
                    else:
                        coords = []


    def close(clicked,root,clicked2):
        directions.append([clicked.get(),clicked2.get()])
        print(directions)
        root.destroy()


#Configureaza o banda sau termina setupul
    index = indexCam
    org_img = testimage
    cv2.namedWindow("road" + str(index))
    cv2.setMouseCallback('road' + str(index), partial(click_event, org_img=org_img, coords=coords))
    image = org_img.copy()
    while True:
        image = org_img.copy()
        image = drawPolygons(image, roads)
        image = drawImage(image, coords)
        cv2.imshow("road" + str(index), image)
        key = cv2.waitKey(1)
        if key == ord("q"):
                #cv2.destroyAllWindows()
                cv2.destroyWindow("road"+str(index))
                return roads, directions
        elif key == ord("s"):
            cv2.destroyWindow("road" + str(index))
            root = Tk()
            root.geometry("200x200")
            options = ["Inainte", "Invers"]
            options2 = ["None", "Stanga", "Dreapta","Inainte","Inainte+Stanga","Inainte+Dreapta"]
            clicked = StringVar()
            clicked2 = StringVar()
            clicked.set("Inainte")
            clicked2.set("None")
            drop = OptionMenu(root, clicked, *options)
            drop2 = OptionMenu(root,clicked2, *options2)
            drop.pack()
            drop2.pack()
            button = Button(root, text="Continua", command=lambda: close(clicked, root,clicked2)).pack()
            root.mainloop()
            coords, roads = finishRoad(coords, roads)
            cv2.namedWindow("road" + str(index))
            cv2.setMouseCallback('road' + str(index), partial(click_event, org_img=org_img, coords=coords))
    #cv2.destroyAllWindows()
    return roads, directions




Instalare

Accesează repository-ul proiectului: https://github.com/AxelPepco/RoadSense
Descarca dezarhiveaza fișierele
Asigura-te ca ai o versiune de Python 3.0 sau mai mare instalată
Deschide un Command Prompt și tastează:
cd "(adresa folderului/RoadSense)"
pip install -r requirements.txt

In "./RoadSense",  vei găsi "MCCode.ino", deschide-l cu compilatorul Arduino si incarca codul pe microprocesorul tău


RoadMap

Inițial, am utilizat un AI de detecție și un tracker (MOSSE Tracker) pentru a urmări traiectoria fiecărei mașini detectate, în scopul de a determina banda și direcția acesteia. Totuși, acest sistem avea limitări, deoarece algoritmul de tracking confunda mașinile care se intersectau, ceea ce afecta acuratețea rezultatelor.

Pentru a îmbunătăți precizia, am introdus funcția de delimitare manuală a benzilor, salvându-le sub formă de poligoane. Astfel, puteam verifica cât din suprafața unei mașini se suprapune cu fiecare bandă delimitată. În plus, pentru a determina sensul de deplasare al mașinilor, am antrenat un model de clasificare folosind YOLO V8 Nano, care oferea o acuratețe ridicată în predicția orientării mașinilor pe ecran. Cu toate acestea, acest model îngreuna semnificativ procesarea unui singur cadru.

În cele din urmă, am optat să delimităm benzile și să le denumim în funcție de caracteristicile lor (de exemplu, bandă cu direcție obligatorie înainte/dreapta, sens înainte/înapoi), dat fiind că acestea sunt deja stabilite. Această abordare a simplificat considerabil procesul de analiză și a îmbunătățit performanța sistemului.

