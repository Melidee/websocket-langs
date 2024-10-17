import socket, os, time
from typing import Optional
from websocket import http
from websocket.http import Request, Response
from websocket.url import Url
from urllib.parse import urlparse
import threading


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
        self.is_masked = len(mask) != 0

    @staticmethod
    def parse(raw_frame: bytes) -> Optional["Frame"]:
        """
        Parses a binary frame into a Frame object

        Args:
            raw_frame (bytes): The binary frame received from a websocket connection
        """
        opcode = int(raw_frame[0] & 0b0000_1111)
        isMasked = bool(raw_frame[1] & 0b1000_0000)
        mask = bytes()
        length = int(raw_frame[1] & 0b01111_111)
        idx = 2
        if length == 126:
            length = int(raw_frame[2:4])
            idx = 4
        elif length == 127:
            length = int(raw_frame[2:10])
            idx = 10
        if isMasked:
            mask = raw_frame[idx : idx + 4]
            idx += 4
        payload = raw_frame[idx:]
        return Frame(opcode, payload, mask)

    def __get_payload(self) -> bytes:
        return self.__payload

    def __set_payload(self, payload: bytes) -> None:
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
            length_ext = bytes()
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
            extensions: A list of extensions on top of the WebSocket connection. Defaults to [].
        """
        self.conn = conn
        self.is_server = is_server
        self.protocols = protocols
        self.extensions = extensions
        self.str_msgs: list[str] = []
        self.bin_msgs: list[bytes] = []
        self.shutdown = False
        self.listen_thread = threading.Thread(
            target=WebSocket._start_listener,
            daemon=True,
            args=(self, self.str_msgs, self.bin_msgs),
        )
        self.listen_thread.start()

    @staticmethod
    def connect(
        url: str,
        protocols: list[str] = [],
        extensions: list[str] = [],
    ) -> Optional["WebSocket"]:
        """Connect to a websocket server and perform an opening handshake

        Args:
            url: the url of the server to connect to
            protocols: an optional list of protocols to request from the server. Defaults to [].
            extensions: an optional list of extensions to request from the server Defaults to [].

        Returns:
            Either an open WebSocket connection, or None if the connection failed
        """
        try:
            server_url = urlparse(url)
        except ValueError as e:
            err = ValueError(f"Failed to parse provided url {url}")
            err.add_note(str(e))
            raise err
        
        conn = socket.create_connection((server_url.hostname, server_url.port), 3)

        req = Request.new_ws(server_url)
        ws_key = req.headers[http.HEADER_WS_KEY]
        conn.sendall(bytes(req))

        data = bytes()
        while len(data) == 0:
            data = conn.recv(2048)
            if not data:
                continue
            res = Response.parse(data.decode("utf-8"))
            if not isinstance(res, Response) or not res.is_valid_ws(ws_key):
                return None
        return WebSocket(
            conn, is_server=False, protocols=protocols, extensions=extensions
        )

    def _start_listener(self, str_msgs, bin_msgs):
        while not self.shutdown:
            buf = bytes()
            while len(buf) == 0:
                try:
                    buf = self.conn.recv(4096)
                except TimeoutError:
                    continue
            frame = Frame.parse(buf)
            if not isinstance(frame, Frame):
                raise IOError("Received invalid data frame from WebSocket connection")
            match frame.opcode:
                case Frame.BINARY:
                    bin_msgs.append(frame.payload)
                case Frame.TEXT:
                    str_msgs.append(frame.payload.decode())
                case Frame.PING:
                    self.pong()
                case Frame.CLOSE:
                    self.close()

    def send(self, msg: bytes) -> None:
        """
        Send binary data over the websocket connection.

        Args:
            msg: The data to send.
        """
        frame = Frame(
            Frame.BINARY, msg, mask=os.urandom(4) if self.is_server else bytes()
        )
        self.conn.sendall(bytes(frame))

    def recv(self) -> bytes | None:
        """
        Receive bytes from the WebSocket connection.

        Returns:
            bytes: The binary data received from the connection.
        """
        if len(self.bin_msgs) == 0:
            return None
        return self.bin_msgs.pop(0)

    def send_text(self, msg: str):
        """
        Send text data over the websocket connection.

        Args:
            msg: The text data to send.
        """
        frame = Frame(
            Frame.TEXT, msg.encode(), mask=os.urandom(4) if self.is_server else bytes()
        )
        self.conn.sendall(bytes(frame))

    def recv_text(self) -> str:
        """
        Receive text from the WebSocket connection.

        Returns:
            str: The binary data received from the connection.
        """
        while len(self.str_msgs) == 0:
            time.sleep(0.25)
        return self.str_msgs.pop(0)

    def close(self):
        self.listen_thread.join()
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.close()


class WebSocketServer:
    def __init__(
        self,
        addr: tuple[str, int] = ("", 80),
        protocols: list[str] = [],
        extensions: list[str] = [],
    ) -> None:
        self.connections: list[WebSocket] = []
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
        if not req.is_valid_ws():
            conn.close()
            return None
        ws_key = req.headers[http.HEADER_WS_KEY]
        res = Response.new_ws(ws_key)
        conn.sendall(str(res).encode("utf-8"))

        ws = WebSocket(
            conn, is_server=True, protocols=self.protocols, extensions=self.extensions
        )
        self.connections.append(ws)
        return ws

    def close(self):
        for conn in self.connections:
            conn.close()
        self.sock.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.close()
