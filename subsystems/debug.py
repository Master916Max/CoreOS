from socket import *
from threading import Thread
import time


class Debuger:
    def __init__(self, kernel,ip = "127.0.0.1", port = 16748):
        self.kernel = kernel
        self.ip = ip
        self.port = port
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.bind((self.ip, self.port))
        self.sock.listen(1)
        self.running = True
        self.connected = False
        self.start()
        print(f"Debuger listening on {self.ip}:{self.port}")
        while not self.connected:
            time.sleep(0.1)

    def start(self):
        self.thread = Thread(target=self.listen, daemon=True)
        self.thread.start()

    def listen(self):
        while self.running:
            try:
                connection, address = self.sock.accept()
                if not self.connected:
                    print(f"Debuger connected to {address}")
                    self.connected = True
                while self.running:
                    data = connection.recv(1024)
                    message = data.decode()
                    print(f"Received message from {address}: {message}")
                    if message == "get_logs":
                        self.kernel.get_all_logs()
                        logs = self.kernel.logs
                        logs_str = "".join(logs.values().__str__()) + "\n"
                        connection.send(logs_str.encode())
            except BlockingIOError:
                pass