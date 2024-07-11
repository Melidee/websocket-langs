import socket
from base64 import b64encode
from websocket.http import Request, Response
from websocket.url import Url


class Websocket:
    def __init__(
        self,
        conn: socket.socket,
        is_server: bool,
        protocols: list[str] = [],
        extensions: list[str] = [],
    ) -> None:
        self.conn = conn
        self.is_server = is_server
        self.protocols = protocols
        self.extensions = extensions

    @staticmethod
    def connect(
        url: str | Url, protocols: list[str] = [], extensions: list[str] = []
    ) -> "Websocket" | None:
        if type(url) is str:
            url = Url.parse(url)
        conn = socket.create_connection(url.hostpair(), 3)

        
        req = Request.new_ws(url)
        ws_key = req.headers["Sec-WebSocket-Key"]

        if protocols != []:
            req.headers["Sec-WebSocket-Protocol"] = ", ".join(protocols)
        if extensions != []:
            req.headers["Sec-WebSocket-Extensions"] = ", ".join(extensions)
        conn.sendall(str(req))

        data = conn.recv(2048)
        if not data:
            return None
        if Response.parse(data).is_valid_ws(ws_key):
            return None
        return Websocket(conn, False, protocols, extensions)


class WebsocketServer:
    def __init__(
        self,
        addr: tuple[str, int] = ("", 8080),
        protocols: list[str] = [],
        extensions: list[str] = [],
    ) -> None:
        self.connections: list[socket.socket] = []
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(addr)
        self.sock.listen()
        self.protocols = protocols
        self.extensions = extensions

    def accept(self) -> Websocket | None:
        conn, _addr = self.sock.accept()
        data = conn.recv(2048)
        if not data:
            conn.close()
            return None

        req = Request.parse(data.decode("utf-8"))
        if req.is_valid_ws():
            conn.close()
            return None
        
        ws_key = req.headers["Sec-WebSocket-Key"]
        res = Response.new_ws(ws_key)
        conn.sendall(str(res).encode("utf-8"))
        return Websocket(conn, is_server=True)

    def close(self):
        for conn in self.connections:
            conn.close()
        self.sock.close()

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.close()

def matching_protocols(
    msg: Request | Response, protocols: list[str], extensions: list[str]
) -> tuple[list[str], list[str]]:
    pass



