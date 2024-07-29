import concurrent.futures
from gui import *
import time
import cv2

lets = ["a", "b", "c"]
ok = True

def count(let):
    c = 0
    while ok:
        c += 1
        print(let + " " + str(c))
        cv2.waitKey(10)
    # Exiting loop, restart count function if ok becomes True again
    if ok:
        start_count_thread(let)

def start_count_thread(let):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.submit(count, let)

def start():
    for let in lets:
        start_count_thread(let)

def add():
    global ok
    img = cv2.imread("./finalinfoed/car.jpg")
    cac = ["d", "e", "f"]
    cnt = 0
    while True:
        cv2.imshow("mumu", img)
        key = cv2.waitKey(1)
        if key == ord("a") and not ok:
            lets.append(cac[cnt])
            cnt += 1
            ok = True  # Set ok back to True to restart count
            start()  # Start count again
        elif key == ord("q"):
            ok = False

if __name__ == "__main__":
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.submit(start)
        executor.submit(add)
