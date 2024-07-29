import socket
import time
def send_data(ip, port, data):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip, port))
    data_string = ','.join(data)
    client_socket.sendall(data_string.encode('utf-8'))
    client_socket.close()

if __name__ == "__main__":
    ip = "127.0.0.1"
    port = 5009
    data = ["Red", "Yellow", "Green", "Red"]
    while True:
        data = ["Green", "Green", "Green", "Green"]
        for i in range(0,5):
            send_data(ip, port, data)
            time.sleep(1)   
        data = ["Red", "Red", "Red", "Red"]
        for i in range(0,5):
            send_data(ip, port, data)
            time.sleep(1)   