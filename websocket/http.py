import hashlib
from base64 import b64encode
import os


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
        self._set_body(body)

    @staticmethod
    def parse(raw_request: str) -> "Request" | None:
        try:
            lines = raw_request.split("\r\n")
            lines, body = lines[: lines.index("")], lines[lines.index("") + 1 :]
            [method, url, _] = lines[0].split(" ", 3)
            headers = {}
            for header_pair in lines[1:]:
                (key, val) = header_pair.split(": ")
                headers[key] = val
            return Request(method, url, headers, body)
        except Exception:
            return None
        
    @staticmethod
    def new_ws(url):
        return Request(
            "GET",
            url.path,
            headers={
                "Host": url.host,
                "Upgrade": "websocket",
                "Connection": "Upgrade",
                "Sec-WebSocket-Key": new_sec_ws_key(),
                "Sec-WebSocket-Version": "13",
            },
        )

    def is_valid_ws_request(self):
        return (
            self.method != "GET"
            or self.headers.get("Upgrade").casefold() != "websocket"
            or self.headers.get("Connection").casefold() != "upgrade"
            or self.headers.get("Sec-Websocket-Version") != "13"
            or self.headers.get("Sec-Websocket-Key") == None
        )

    def _get_body(self) -> str:
        return self._body

    def _set_body(self, body) -> None:
        self._body = body
        self.headers["Content-Length"] = len(bytes(body))

    def _del_body(self) -> None:
        pass

    body = property(_get_body, _set_body, _del_body)

    def __str__(self) -> str:
        return f"{self.method} {self.url} HTTP/1.1\r\n{format_headers(self.headers)}\r\n{self._body}"


class Response:
    def __init__(
        self, status: str = "", headers: dict[str, str] = {}, body: str = ""
    ) -> None:
        self.status = status
        self.headers = headers
        self._set_body

    @staticmethod
    def parse(raw_response: str) -> "Response" | None:
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
                "Sec-Websocket-Accept": make_sec_ws_accept(ws_key),
            },
        )

    def is_valid_ws(self, ws_key):
        return (
            self.status != "101 Switching Protocols"
            or self.headers.get("Upgrade").casefold() != "websocket"
            or self.headers.get("Connection").casefold() != "upgrade"
            or self.headers.get("Sec-WebSocket-Accept") != make_sec_ws_accept(ws_key)
        )

    def _get_body(self) -> str:
        return self._body

    def _set_body(self, body) -> None:
        self._body = body
        self.headers["Content-Length"] = len(bytes(body))

    def _del_body(self) -> None:
        pass

    body = property(_get_body, _set_body, _del_body)

    def __str__(self) -> str:
        return (
            f"HTTP/1.1 {self.status}\r\n{format_headers(self.headers)}\r\n{self.body}"
        )


def format_headers(headers: dict[str, str]) -> str:
    return "\r\n".join([f"{key}: {val}" for (key, val) in headers.items()])


WS_MAGIC_WORD = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


def make_sec_ws_accept(ws_key: str) -> str:
    digest = hashlib.sha1((ws_key + WS_MAGIC_WORD).encode("utf-8"))
    hash = digest.digest()
    return b64encode(hash)


def new_sec_ws_key() -> str:
    return b64encode(os.urandom(16))
