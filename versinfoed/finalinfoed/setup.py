from selectroad import *
from roadfunc import *

def SetUp(img):
    img = procesareRoad(img)

    #cv2.imshow("a",img)
    #cv2.waitKey(0)
    roadPoints,directions = SelectPoints(img)

    return roadPoints,directions


