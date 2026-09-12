import socket


client = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

client.connect(
    ("127.0.0.1", 16748)
)

path = "Kernel"

try:
    while True:
        message = input(f"Debug-{path}> ")

        if message.lower() == "exit":
            break

        client.sendall(
            message.encode("utf-8")
        )

        data = client.recv(4096)

        if not data:
            print("Debugger disconnected.")
            break

        print(data.decode("utf-8"))

finally:
    client.close()