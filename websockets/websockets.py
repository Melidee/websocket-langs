import socket
from typing import Optional

class Websocket:
    pass

class WebsocketServer:
    def __init__(self, addr: tuple[str, int]) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(addr)
        self.sock.listen()

    def accept(self) -> Optional[Websocket]:
        conn, _addr = self.sock.accept()
        data = conn.recv(2048)
        if not data:
            return None    

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.close()

    def close(self):
        self.sock.close()

