from vehiclefunc import *
from setup import *
from carsonroad import *
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

def Processing():
    MAX_FRAMES = 1000
    N = 2
    THRESH = 30
    ASSIGN_VALUE = 255 #Value to assign the pixel if the threshold is met
    cap = cv2.VideoCapture("cars.mp4")

    i = 1
    roadPoints = []
    lanes = np.zeros_like(roadPoints)
    car_p = []


    t=0
    for t in range(MAX_FRAMES):
        ret, frame = cap.read()
        _,cnt,car_p = DetectCars(frame, t)
        print(cnt)
        if cnt == 0 and t>10:
            roadPoints,directions = SetUp(frame)
            break

    with open ("coords.txt","w") as file:
        file.write(str(roadPoints))

    # roadPoints = [[[205, 718], [738, 151], [1014, 154], [701, 718]], [[706, 719], [1025, 160], [1276, 148], [1252, 719]]]
    # directions = ["Inainte", "Invers"]

    for t in range(MAX_FRAMES):
        ret, frame = cap.read()
        frame ,cnt,car_p = DetectCars(frame, t)
        incoming = 0
        leaving = 0
        for car in car_p:
            x_min,y_min,x_max,y_max = car
            # carPoint = Point((x_max+x_min)/2,y_max )
            w,h = x_max-x_min,y_max-y_min
            carPol = Polygon([(x_min,y_min), (x_max,y_min),(x_max,y_max), (x_min, y_max)])
            percs = np.zeros_like(directions)
            for i in range(0,len(roadPoints)):
                polygon = Polygon(roadPoints[i])
                intersection_area = carPol.intersection(polygon).area

    # Calculate the percentage of intersection relative to the area of polygon1
                percentage_intersection = (intersection_area / carPol.area) * 100
                percs[i] = percentage_intersection
                # if polygon.contains(carPoint):
                #     if directions[i] == "Inainte":
                #         leaving+=1
                #     elif directions[i] == "Invers":
                #         incoming+=1
            print(len(car_p))
            max_index = np.argmax(percs)
            if directions[max_index] == "Inainte":
                    leaving+=1
            elif directions[max_index] == "Invers":
                    incoming+=1
            frame = cv2.putText(frame,directions[max_index]+ ", " + percs[max_index],(x_min,y_min),cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),1)

        print(incoming,leaving)
        cv2.imshow("frame", frame)
        cv2.waitKey(40)
            #check overlap
            #add to lanes
        


        




