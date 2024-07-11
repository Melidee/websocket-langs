class Request:
    def __init__(self, method: str = "GET", url: str = "/", headers: dict[str, str] = {}, body: str = "") -> None:
        self.method: str = method
        self.url: str = url
        self.headers: dict[str, str] = headers
        self._set_body(body)

    @staticmethod
    def parse(raw_request: str) -> "Request":
        lines = raw_request.split("\r\n")
        lines, body = lines[:lines.index("")], lines[lines.index("")+1:]
        [method, url, _] = lines[0].split(" ", 3)
        headers = {}
        for header_pair in lines[1:]:
            (key, val) = header_pair.split(": ")
            headers[key] = val
        return Request(method, url, headers, body)

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
    def __init__(self, status: str = "", headers: dict[str, str] = {}, body: str = "") -> None:
        self.status = status
        self.headers = headers
        self._set_body

    @staticmethod
    def parse(raw_response: str):
        lines = raw_response.split("\r\n")
        lines, body = lines[:lines.index("")], lines[lines.index("")+1:]
        [_, status] = lines[0].split(" ")
        headers = {}
        for header_pair in lines[1:]:
            (key, val) = header_pair.split(": ")
            headers[key] = val
        return Response(status, headers, body)
    def _get_body(self) -> str:
        return self._body
    
    def _set_body(self, body) -> None:
        self._body = body
        self.headers["Content-Length"] = len(bytes(body))

    def _del_body(self) -> None:
        pass

    body = property(_get_body, _set_body, _del_body)

    def __str__(self) -> str:
        return f"HTTP/1.1 {self.status}\r\n{format_headers(self.headers)}\r\n{self.body}"

def format_headers(headers: dict[str, str]) -> str:
    return "\r\n".join([f"{key}: {val}" for (key, val) in headers.items()])