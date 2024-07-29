import cv2
import numpy as np
import socket
import struct
import time

global unityframes
unityframes = []

def connect_to_server(address, port, retry_interval=5, max_retries=50):
    retries = 0
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((address, port))
            print(f"Connected to server at {address}:{port}")
            return sock
        except ConnectionRefusedError:
            retries += 1
            print(f"Connection refused, retrying in {retry_interval} seconds... (Attempt {retries}/{max_retries})")
            time.sleep(retry_interval)
    
    print("Max retries reached. Unable to connect to the server.")
    return None

def receive_data(sock, size):
    data = bytearray()
    while len(data) < size:
        packet = sock.recv(size - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data

def receive_frame(sock):

    # Read the size of the frame
    size_data = receive_data(sock, 4)
    if size_data is None:
        return None
    frame_size = struct.unpack('!I', size_data)[0]

    # Read the frame data
    frame_data = receive_data(sock, frame_size)
    if frame_data is None:
        return None

    # Convert the frame data to a numpy array
    np_frame = np.frombuffer(frame_data, dtype=np.uint8)

    # Decode the numpy array into an image
    frame = cv2.imdecode(np_frame, cv2.IMREAD_COLOR)
    return frame

def LoadingFrames(IP,PORT):
    print("Am inceput")
    global unityframes
    server_address = IP
    server_port = PORT

    sock = connect_to_server(server_address, server_port)
    if sock is not None:
       # exit("Unable to connect to the server. Exiting...")
    
        while True:

            camframe = receive_frame(sock)


            if camframe is None:
                print("Failed to receive unityframes from all cameras")
            
            cv2.imshow('North Camera', camframe)

            cv2.waitKey(1)


