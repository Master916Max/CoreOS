import socket
from threading import Thread


class Debugger:
    def __init__(self, kernel, ip="127.0.0.1", port=16748):
        self.kernel = kernel
        self.ip = ip
        self.port = port

        self.running = False
        self.connections = []

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Allows the port to be reused after CoreOS shuts down.
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.sock.bind((self.ip, self.port))
        self.sock.listen(5)

        # Allows shutdown() to interrupt accept().
        self.sock.settimeout(1.0)

        self.start()

    def start(self):
        if self.running:
            return

        self.running = True

        self.thread = Thread(
            target=self.listen,
            daemon=True
        )

        self.thread.start()

        print(
            f"Debugger listening on "
            f"{self.ip}:{self.port}"
        )


    def listen(self):
        while self.running:
            try:
                connection, address = self.sock.accept()

                print(
                    f"Debugger connected: {address}"
                )

                self.connections.append(connection)

                Thread(
                    target=self.handle_connection,
                    args=(connection, address),
                    daemon=True
                ).start()

            except socket.timeout:
                continue

            except OSError:
                if self.running:
                    raise

    def handle_connection(self, connection, address):
        try:
            while self.running:

                data = connection.recv(4096)

                if not data:
                    break

                message = data.decode("utf-8").strip()

                print(
                    f"Debugger [{address}]: "
                    f"{message}"
                )

                response = self.parse_command(message)

                if response is not None:
                    connection.sendall(
                        response.encode("utf-8")
                    )

        except ConnectionResetError:
            pass

        finally:
            if connection in self.connections:
                self.connections.remove(connection)

            connection.close()

            print(
                f"Debugger disconnected: {address}"
            )

    def parse_command(self, message):
        parts = message.split()

        if not parts:
            return ""

        command = parts[0].lower()
        args = parts[1:]

        if command == "get_logs":
            return self.cmd_get_logs(args)

        if command == "help":
            return self.cmd_help(args)

        return f"Unknown command: {command}\n"

    def cmd_get_logs(self, args):
        self.kernel.get_all_logs()

        logs = self.kernel.logs

        return str(logs) + "\n"

    def cmd_help(self, args):
        return (
            "CoreOS Debugger\n"
            "\n"
            "Commands:\n"
            "  help\n"
            "  get_logs\n"
        )

    def stop(self):
        if not self.running:
            return

        print("Stopping debugger...")

        self.running = False

        for connection in self.connections:
            try:
                connection.shutdown(socket.SHUT_RDWR)
                connection.close()
            except OSError:
                pass

        self.connections.clear()

        try:
            self.sock.close()
        except OSError:
            pass