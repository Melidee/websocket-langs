import socket, os
from websocket.http import Request, Response
from websocket.url import Url


class Frame:

    CONTINUE = 0x0
    TEXT = 0x1
    BINARY = 0x2
    CLOSE = 0x8
    PING = 0x9
    PONG = 0xA

    def __init__(self, opcode: int, payload: bytes, mask: bytes = bytes([])) -> None:
        """
        Constructs a new Frame object.

        Args:
            opcode (int): The opcode specifying the kind of message, use one of the Frame
                    constants such as `Frame.TEXT`
            payload (bytes): The data contained by this frame
            mask (bytes): The mask key, either an empty `bytes` object if not masking or a  
                    `bytes` object of length 4
        """
        self.opcode = opcode
        self.__payload = payload
        self.length: int = len(payload)
        self.__mask = mask
        self.is_masked = len(mask) == 0

    @staticmethod
    def parse(raw_frame: bytes) -> "Frame" | None:
        """
        Parses a binary frame into a Frame object

        Args:
            raw_frame (bytes): The binary frame recieved from a websocket connection
        """
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
        """
        Converts the frame to a byte array to be sent over the network

        Returns:
            bytes: The finalized bytes
        """
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


class WebSocket:
    """
    A Websocket connection as specified by RFC 6455
    """
    def __init__(
        self,
        conn: socket.socket,
        is_server: bool,
        protocols: list[str] = [],
        extensions: list[str] = [],
    ) -> None:
        """
        Constructs a `WebSocket` connection from parts, note that `WebSocket` should usually 
        not be constructed directly, and users should instead use `Websocket.connect()`
        to open client side connections, or use a `WebSocketServer` to open server side
        connections.

        Args:
            conn: A TCP connection for the websocket connection, assumes 
                    a websocket handshake has already been performed.
            is_server: Describes if the connection is from a server or client.
            protocols: A list of protocols on top of the WebSocket connection. Defaults to [].
            extensions: A list of extentions on top of the WebSocket connection. Defaults to [].
        """
        self.conn = conn
        self.is_server = is_server
        self.protocols = protocols
        self.extensions = extensions

    @staticmethod
    def connect(
        url: str | Url, protocols: list[str] = [], extensions: list[str] = []
    ) -> "WebSocket" | None:
        """Connect to a websocket server and perform an opening handshake

        Args:
            url: the url of the server to connect to
            protocols: an optional list of protocols to request from the server. Defaults to [].
            extentions: an optional list of extentions to request from the server Defaults to [].

        Returns:
            Either an open WebSocket connection, or None if the connection failed
        """
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
        return WebSocket(conn, False, protocols, extensions)

    def send(self, msg: bytes) -> None:
        """
        Send binary data over the websocket connection.

        Args:
            msg: The data to send.
        """
        frame = Frame(Frame.BINARY, msg, mask=os.urandom(4) if self.is_server else bytes())
        self.conn.sendall(bytes(frame))

    def recv(self, continues=bytes()) -> bytes:
        """
        Recieve bytes from the WebSocket connection.

        Returns:
            bytes: The binary data recieved from the connection.
        """
        buf = bytes()
        while buf:
            buf = self.conn.recv(4096)
            data += buf
        frame = Frame.parse(data)
        if frame.opcode == Frame.CONTINUE:
            return self.recv(continues=continues+frame.payload)
        return continues + frame.payload

    def send_text(self, msg: str):
        """
        Send text data over the websocket connection.

        Args:
            msg: The text data to send.
        """
        frame = Frame(Frame.TEXT, msg, mask=os.urandom(4) if self.is_server else bytes())
        self.conn.sendall(bytes(frame))

    def recv_text(self, continues="") -> str:
        """
        Recieve bytes from the WebSocket connection.

        Returns:
            str: The binary data recieved from the connection.
        """
        buf = bytes()
        while buf:
            buf = self.conn.recv(4096)
            data += buf
        frame = Frame.parse(data)
        if frame.opcode == Frame.CONTINUE:
            return self.recv(continues=continues+frame.payload)
        return continues + frame.payload

    def close(self):
        self.conn.close()

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.close()


class WebSocketServer:
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

    def accept(self) -> WebSocket | None:
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

        ws = WebSocket(conn, True, self.protocols, self.extensions)
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
