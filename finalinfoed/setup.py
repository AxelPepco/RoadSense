from selectroad import *
from roadfunc import procesareRoad

def SetUp(img,index):
    img = procesareRoad(img)
    print("AM TERMINAT PROCESAREA ROAD AAAAAAAAAAA")
    #cv2.imshow("a",img)
    #cv2.waitKey(0)
    roadPoints,directions = SelectPoints(img,index)

    return roadPoints,directions


