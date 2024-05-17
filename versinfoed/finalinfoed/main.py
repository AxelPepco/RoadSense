import concurrent.futures
import time
import cv2
from gui import*




if __name__ == "__main__":
    thread_count = 0
    img = cv2.imread("./finalinfoed/car.jpg")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.submit(createGui,executor)
        while True:
            pass
            time.sleep(10)
