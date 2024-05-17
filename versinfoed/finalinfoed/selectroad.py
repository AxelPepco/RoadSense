
from tkinter import *
from tkinter import ttk
from roadfunc import *
from vehiclefunc import *
from PIL import Image, ImageTk

import cv2


global coords
global directions
global roads
global org_img
global root
global clicked
directions = []
roads = []
coords = []

def finishRoad():
    global coords
    global roads
    if len(coords) > 2:
        polygon = []
        for point in coords:
            polygon.append(point)  # No need to convert to tuple
        roads.append(polygon) 
        coords = []

def drawPolygons(image):
    global roads
    if roads:
        for road in roads:
            pts = np.array(road, np.int32)  # Convert to NumPy array of integers
            pts = pts.reshape((-1, 1, 2))    # Reshape for fillPoly
            cv2.fillPoly(image, [pts], color=(0, 255, 0,128))  # Wrap pts in a list
            #cv2.addWeighted(overlay, 128, image, 1 - 0.5, 0, image)  # Blend overlay with original image
    
    return image

def drawImage(img):
    global roads,coords
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

def click_event(event, x, y, flags, params):
    global image, coords, roads,directions
    if event == cv2.EVENT_LBUTTONDOWN:
        coords.append([x, y])
        print(coords)
        image = org_img.copy()  
        image = drawPolygons(image)
        image = drawImage(image)
        cv2.imshow("road", image)

    if event == cv2.EVENT_RBUTTONDOWN:
        if coords:
            coords.pop()
            print(coords)
            image = org_img.copy() 
            image = drawImage(image)
            cv2.imshow("road", image)
        else:
            roads.pop()
            directions.pop()
            coords = roads[len(roads)]

def close():
    global root,clicked 
    directions.append(clicked.get())
    print(directions)
    root.destroy()

def SelectPoints(testimage):
    global org_img
    global roads
    global coords
    roads = []
    coords = []
    org_img = testimage
    cv2.namedWindow("road")
    cv2.setMouseCallback('road', click_event)
    image = org_img.copy() 
    while True:
        image = org_img.copy() 
        image = drawPolygons(image)
        image = drawImage(image)
        cv2.imshow("road", image)
        key = cv2.waitKey(1)
        if key == ord("q"):
            break
        elif key == ord("s"):
            cv2.destroyWindow("road")
            global root,clicked
            root = Tk()
            root.geometry("200x200")
            options = ["Inainte", "Invers"]
            clicked = StringVar()
            clicked.set("Inainte")
            drop = OptionMenu(root,clicked,*options)
            drop.pack()
            button = Button(root,text = "Continua", command=close).pack()
            root.mainloop()
            finishRoad()
            cv2.namedWindow("road")
            cv2.setMouseCallback('road', click_event)
    cv2.destroyAllWindows()
    return roads,directions