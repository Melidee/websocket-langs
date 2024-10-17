import hashlib, os
from base64 import b64encode, b64decode
from typing import Optional

HEADER_WS_VERSION = "Sec-WebSocket-Version"
HEADER_WS_KEY = "Sec-WebSocket-Key"
HEADER_WS_ACCEPT = "Sec-WebSocket-Accept"
HEADER_WS_PROTOCOL = "Sec-WebSocket-Protocol"
HEADER_WS_EXTENSIONS = "Sec-WebSocket-Extensions"


class Request:
    def __init__(
        self,
        method: str = "GET",
        url: str = "/",
        headers: dict[str, str] = {},
        body: str = "",
    ) -> None:
        self.method: str = method
        self.url: str = url
        self.headers: dict[str, str] = headers
        self._body = ""
        self._set_body(body)

    @staticmethod
    def parse(raw_request: str) -> "Request":
        lines = raw_request.split("\r\n")
        try:
            lines, body_splits = lines[: lines.index("")], lines[lines.index("") + 1 :]
        except ValueError:
            raise ValueError("No trailing line after headers")
        body = "\r\n".join(body_splits)
        try:
            method, url, proto = lines[0].split(" ")
        except (ValueError, IndexError):
            raise ValueError(f"Invalid first line of request: {lines[0]}")
        if proto != "HTTP/1.1" and proto != "HTTP/1.0":
            raise ValueError("Invalid HTTP protocol specified by request")
        headers = {}
        for header_pair in lines[1:]:
            try:
                key, val = header_pair.split(": ")
                headers[key] = val
            except ValueError:
                raise ValueError(f"Invalid Header format: {header_pair}")
        return Request(method, url, headers, body)

    @staticmethod
    def new_ws(url):
        return Request(
            "GET",
            url.path,
            headers={
                "Host": url.host,
                "Upgrade": "websocket",
                "Connection": "Upgrade",
                HEADER_WS_KEY: new_sec_ws_key(),
                HEADER_WS_VERSION: "13",
            },
        )

    def is_valid_ws(self):
        return (
            self.method == "GET"
            and self.headers.get("Host") != None
            and self.headers.get("Upgrade") == "websocket"
            and self.headers.get("Connection") == "Upgrade"
            and self.headers.get(HEADER_WS_VERSION) == "13"
            and self.headers.get(HEADER_WS_KEY) != None
        )

    def _get_body(self) -> str:
        return self._body

    def _set_body(self, body) -> None:
        self._body = body
        self.headers["Content-Length"] = str(len(body.encode("utf-8")))

    def _del_body(self) -> None:
        del self._body

    body = property(_get_body, _set_body, _del_body)

    def __str__(self) -> str:
        return f"{self.method} {self.url} HTTP/1.1\r\n{format_headers(self.headers)}\r\n{self._body}"

    def __bytes__(self) -> bytes:
        return str(self).encode("utf-8")

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Request)
            and self.method == other.method
            and self.url == other.url
            and self.headers == other.headers
            and self.body == other.body
        )


class Response:
    def __init__(
        self, status: str = "", headers: dict[str, str] = {}, body: str = ""
    ) -> None:
        self.status = status
        self.headers = headers
        self._body = body

    @staticmethod
    def parse(raw_response: str) -> Optional["Response"]:
        lines = raw_response.split("\r\n")
        lines, body_splits = lines[: lines.index("")], lines[lines.index("") + 1 :]
        body = "\r\n".join(body_splits)
        try:
            _proto, status = lines[0].split(" ", 1)
        except (ValueError, IndexError):
            raise ValueError(f"Invalid first line of response: {lines[0]}")
        headers = {}
        for header_pair in lines[1:]:
            try:
                (key, val) = header_pair.split(": ")
            except ValueError:
                raise ValueError(f"Invalid Header format: {header_pair}")
            headers[key] = val
        return Response(status, headers, body)

    @staticmethod
    def new_ws(ws_key: str):
        return Response(
            "101 Switching Protocols",
            headers={
                "Upgrade": "websocket",
                "Connection": "Upgrade",
                HEADER_WS_ACCEPT: make_sec_ws_accept(ws_key),
            },
        )

    def is_valid_ws(self, ws_key):
        return (
            self.status == "101 Switching Protocols"
            and self.headers.get("Upgrade").casefold() == "websocket"
            and self.headers.get("Connection").casefold() == "upgrade"
            and self.headers.get(HEADER_WS_ACCEPT) == make_sec_ws_accept(ws_key)
        )

    def _get_body(self) -> str:
        return self._body

    def _set_body(self, body) -> None:
        self._body = body
        self.headers["Content-Length"] = str(len(bytes(body)))

    def _del_body(self) -> None:
        del self._body

    body = property(_get_body, _set_body, _del_body)

    def __str__(self) -> str:
        return (
            f"HTTP/1.1 {self.status}\r\n{format_headers(self.headers)}\r\n{self.body}"
        )

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Response)
            and self.status == other.status
            and self.headers == other.headers
            and self.body == other.body
        )


def format_headers(headers: dict[str, str]) -> str:
    return "\r\n".join([f"{key}: {val}" for (key, val) in headers.items()])


WS_MAGIC_WORD = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


def make_sec_ws_accept(ws_key: str) -> str:
    digest = hashlib.sha1((ws_key + WS_MAGIC_WORD).encode())
    hash = digest.digest()
    return b64encode(hash).decode()


def new_sec_ws_key() -> str:
    return b64encode(os.urandom(16)).decode()
