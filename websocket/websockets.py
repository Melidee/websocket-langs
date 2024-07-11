import socket, hashlib, os
from base64 import b64encode
from typing import Optional
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
        ws_key = new_sec_ws_key()
        req = Request(
            "GET",
            url.path,
            headers={
                "Host": url.host,
                "Upgrade": "websocket",
                "Connection": "Upgrade",
                "Sec-WebSocket-Key": ws_key,
                "Sec-WebSocket-Version": "13",
            },
        )
        if protocols != []:
            req.headers["Sec-WebSocket-Protocol"] = ", ".join(protocols)
        if extensions != []:
            req.headers["Sec-WebSocket-Extensions"] = ", ".join(extensions)
        conn.sendall(str(req))
        data = conn.recv(2048)
        if not data:
            return None
        res = Response.parse(data)
        if is_valid_response(res, ws_key):
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
        self.sock.create_serve
        self.sock.listen()

    def accept(self) -> Optional[Websocket]:
        conn, _addr = self.sock.accept()
        data = conn.recv(2048)
        if not data:
            return None
        req = Request.parse(data.decode("utf-8"))
        if is_valid_request(req):
            conn.close()
            return None
        ws_key = req.headers["Sec-WebSocket-Key"]
        res = Response(
            status="101 Switching Protocols",
            headers={
                "Upgrade": "websocket",
                "Connection": "Upgrade",
                "Sec-Websocket-Accept": make_sec_ws_accept(ws_key),
            },
        )
        conn.sendall(str(res).encode("utf-8"))
        return Websocket(conn, is_server=True)

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.close()

    def close(self):
        for conn in self.connections:
            conn.close()
        self.sock.close()


def is_valid_request(req) -> bool:
    return (
        req.method != "GET"
        or req.headers.get("Upgrade").casefold() != "websocket"
        or req.headers.get("Connection").casefold() != "upgrade"
        or req.headers.get("Sec-Websocket-Version") != "13"
        or req.headers.get("Sec-Websocket-Key") == None
    )


def is_valid_response(res, ws_key) -> bool:
    return (
        res.status != "101 Switching Protocols"
        or res.headers.get("Upgrade").casefold() != "websocket"
        or res.headers.get("Connection").casefold() != "upgrade"
        or res.headers.get("Sec-WebSocket-Accept") != make_sec_ws_accept(ws_key)
    )


def parse_extensions(ext: str) -> None:
    pass


def new_sec_ws_key() -> str:
    return b64encode(os.urandom(16))


WS_MAGIC_WORD = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


def make_sec_ws_accept(ws_key: str) -> str:
    digest = hashlib.sha1((ws_key + WS_MAGIC_WORD).encode("utf-8"))
    hash = digest.digest()
    return b64encode(hash)
