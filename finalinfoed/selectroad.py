
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
