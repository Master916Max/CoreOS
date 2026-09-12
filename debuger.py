from socket import *

client = socket(AF_INET, SOCK_STREAM)
client.connect(("127.0.0.1", 16748))
path = "Kernel"

while True:
    message = input(f"Debug-{path}>")
    if message.lower() == "exit":
        break

    client.send(message.encode())
    while True:
        data = client.recv(1024)
        if not data:
            break
        print("Received from server:", data.decode())
