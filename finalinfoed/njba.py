import threading
import time
import cv2

def my_function(thread_num):
    print(f"Thread {thread_num} is running...")
    # Simulate some task
    time.sleep(2)
    print(f"Thread {thread_num} finished.")

def add_thread():
    global thread_count
    thread_count += 1
    thread = threading.Thread(target=my_function, args=(thread_count,))
    thread.start()
    print(f"Added thread {thread_count}")

if __name__ == "__main__":
    thread_count = 0
    img = cv2.imread("./finalinfoed/car.jpg")
    while True:
            cv2.imshow("a",img)
            key = cv2.waitKey(1)
            if key == ord("q"):
                break
            elif key == ord("a"):

                add_thread()

