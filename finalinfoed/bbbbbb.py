from camercam import CameraCam
import concurrent.futures
import keyboard
import time

camera1 = CameraCam(0)
camera2 = CameraCam(1)

cameras = [camera1, camera2]

def InitCam(camera, index, max_retries=5, delay=1):
    attempts = 0
    while attempts < max_retries:
        try:
            camera.SetUpCam()
            camera.quit()
            camera.processing = True
            camera.Processing()
            return  # Exit the function if successful
        except Exception as e:
            print(f"Error in camera at index {index}: {e}")
            if "Infer Request is busy" in str(e):
                attempts += 1
                print(f"Retrying {index} in {delay} seconds... ({attempts}/{max_retries})")
                time.sleep(delay)  # Wait before retrying
            else:
                break  # For other exceptions, do not retry

with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = [executor.submit(InitCam, cam, idx) for idx, cam in enumerate(cameras)]
    
    # Wait for the results and handle exceptions
    for future in concurrent.futures.as_completed(futures):
        try:
            future.result()  # This will re-raise any exception caught during thread execution
        except Exception as e:
            print(f"Exception caught from thread: {e}")
