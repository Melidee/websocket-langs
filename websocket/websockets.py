import socket, hashlib
from base64 import b64encode
from typing import Optional
from websocket.http import Request, Response

class Websocket:
    def __init__(self, conn: socket.socket, is_server: bool) -> None:
        pass
        
    @staticmethod
    def connect(addr: tuple[str, int]) -> "Websocket" | None:
        conn = socket.create_connection(addr, 3)
        req = Request("GET", "/", headers={
            "Upgrade": "websocket",
            "Connection": "Upgrade",
            "Sec-Websocket-Key": "",
            "Sec-Websocket-Version": "13",
        })
        conn.sendall(str(req))
        data = conn.recv(2048)
        if not data:
            return None
        res = Response.parse(data)

    @staticmethod
    def from_server() -> "Websocket":
        pass

class WebsocketServer:
    def __init__(self, addr: tuple[str, int] = ('', 8080)) -> None:
        self.connections: list[socket.socket] = []
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.create_serve
        self.sock.listen()
        

    def accept(self) -> Optional[Websocket]:
        conn, _addr = self.sock.accept()
        data = conn.recv(2048)
        if not data:
            return None
        req = Request.parse(data.decode('utf-8'))
        if req.method != "GET" \
            or req.headers.get("Upgrade") != "websocket" \
            or req.headers.get("Connection") != "Upgrade" \
            or req.headers.get("Sec-Websocket-Version") != "13" \
            or (ws_key := req.headers.get("Sec-Websocket-Key")) == None:
            conn.close()
            return None
        res = Response(status="101 Switching Protocols", headers={
            "Upgrade": "websocket",
            "Connection": "Upgrade",
            "Sec-Websocket-Accept": make_sec_ws_accept(ws_key),
        })
        conn.sendall(str(res).encode('utf-8'))
        return Websocket.from_server()

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.close()

    def close(self):
        for conn in self.connections:
            conn.close()
        self.sock.close()

WS_MAGIC_WORD = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
def make_sec_ws_accept(ws_key: str) -> str:
    digest = hashlib.sha1((ws_key + WS_MAGIC_WORD).encode("utf-8"))
    hash = digest.digest()
    return b64encode(hash)
