import socket
from base64 import b64encode
from websocket.http import Request, Response
from websocket.url import Url


class Frame:
    OPCODE_CONTINUE = 0x0
    OPCODE_TEXT = 0x1
    OPCODE_BINARY = 0x2
    OPCODE_CLOSE = 0x8
    OPCODE_PING = 0x9
    OPCODE_PONG = 0xA

    def __init__(self, opcode: int, payload: bytes, mask: bytes) -> None:
        self.opcode = opcode
        self.__payload = payload
        self.length: int = len(payload)
        self.__mask = mask
        self.is_masked = len(mask) == 0

    @staticmethod
    def parse(raw_frame) -> "Frame" | None:
        pass

    def __get_payload(self) -> str:
        return self.__payload

    def __set_payload(self, payload) -> None:
        self.__payload = payload
        self.length = len(payload)

    def __del_payload(self) -> None:
        del self.__payload

    payload = property(__get_payload, __set_payload, __del_payload)

    def __get_mask(self):
        return self.__mask

    def __set_mask(self, mask):
        self.__mask = mask

    def __del_mask(self):
        del self.__mask

    mask = property(__get_mask, __set_mask, __del_mask)

    def __bytes__(self) -> bytes:
        fin = 0b1000_0000
        mask = 0b1000_0000 if self.is_masked else 0
        if self.length >= 65536:
            length_ext = bytes(self.length)
            length = 127
        elif self.length > 125:
            length_ext = bytes(self.length)
            length = 126
        else:
            length_ext = []
            length = self.length
        return bytes(
            [fin | self.opcode, mask | length, *length_ext, *self.mask, *self.payload]
        )


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

    def send(msg: bytes):
        pass

    def recv() -> bytes:
        pass

    def send_text(msg: str):
        pass

    def recv_text() -> str:
        pass

    def close(self):
        self.conn.close()

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.close()


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

        ws = Websocket(conn, True, self.protocols, self.extensions)
        self.connections.append(ws)
        return ws

    def close(self):
        for conn in self.connections:
            conn.close()
        self.sock.close()

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.close()
