import hashlib, os
from base64 import b64encode
from typing import Self

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
    def parse(raw_request: str) -> Self:
        lines = raw_request.split("\r\n")
        try:
            lines, body = lines[: lines.index("")], lines[lines.index("") + 1 :]
        except ValueError:
            raise ValueError("No trailing line after headers")
        body = "\r\n".join(body)
        try:
            method, url, proto = lines[0].split(" ")
        except ValueError or IndexError:
            raise ValueError(f"Invalid first line of request: {lines[0]}")
        if proto != "HTTP/1.1" or proto != "HTTP/1.0":
            raise ValueError("Invalid HTTP protocol specified by request")
        headers = {}
        for header_pair in lines[1:]:
            try:
                key, val = header_pair.split(": ", 1)
            except ValueError:
                ValueError(f"Invalid Header format: {header_pair}")
            headers[key] = val
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

    def is_valid_ws_request(self):
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

    def __eq__(self, other: object) -> bool:
        try:
            return (
                self.method == other.method
                and self.url == other.url
                and self.headers == other.headers
                and self.body == other.body
            )
        except AttributeError:
            return False


class Response:
    def __init__(
        self, status: str = "", headers: dict[str, str] = {}, body: str = ""
    ) -> None:
        self.status = status
        self.headers = headers
        self._body = body

    @staticmethod
    def parse(raw_response: str) -> Self | None:
        try:
            lines = raw_response.split("\r\n")
            lines, body = lines[: lines.index("")], lines[lines.index("") + 1 :]
            [_, status] = lines[0].split(" ")
            headers = {}
            for header_pair in lines[1:]:
                (key, val) = header_pair.split(": ")
                headers[key] = val
            return Response(status, headers, body)
        except Exception:
            return None

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
            self.status != "101 Switching Protocols"
            or self.headers.get("Upgrade").casefold() != "websocket"
            or self.headers.get("Connection").casefold() != "upgrade"
            or self.headers.get(HEADER_WS_ACCEPT) != make_sec_ws_accept(ws_key)
        )

    def _get_body(self) -> str:
        return self._body

    def _set_body(self, body) -> None:
        self._body = body
        self.headers["Content-Length"] = len(bytes(body))

    def _del_body(self) -> None:
        del self._body

    body = property(_get_body, _set_body, _del_body)

    def __str__(self) -> str:
        return (
            f"HTTP/1.1 {self.status}\r\n{format_headers(self.headers)}\r\n{self.body}"
        )

    def __eq__(self, other: object) -> bool:
        try:
            return (
                self.status == other.status
                and self.headers == other.headers
                and self.body == other.body
            )
        except AttributeError:
            return False


def format_headers(headers: dict[str, str]) -> str:
    return "\r\n".join([f"{key}: {val}" for (key, val) in headers.items()])


WS_MAGIC_WORD = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


def make_sec_ws_accept(ws_key: str) -> str:
    digest = hashlib.sha1((ws_key + WS_MAGIC_WORD).encode("utf-8"))
    hash = digest.digest()
    return b64encode(hash)


def new_sec_ws_key() -> str:
    return b64encode(os.urandom(16))
