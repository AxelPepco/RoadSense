import concurrent.futures
import time
import cv2
from gui import*


#Ruleaza GUI-ul pe propriul sau thread

if __name__ == "__main__":
    thread_count = 0
    img = cv2.imread("./finalinfoed/car.jpg")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.submit(create_gui,executor)
        while True:
            pass
            time.sleep(10)