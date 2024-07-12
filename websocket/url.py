from typing import Self

class Url:
    def __init__(
        self,
        scheme: str,
        host: str,
        port: str,
        path: str = "",
        query: dict[str, str] = {},
        fragment: str = "",
    ) -> None:
        self.scheme = scheme
        self.host = host
        self.port = port
        self.path = path
        self.query = query
        self.fragment = fragment

    @staticmethod
    def parse(raw_url: str) -> Self | None:
        """
        Parses a URL from a string

        Returns:
            Self | None: A `Url` object if parsing is successful, or `None` if parsing fails
        """
        [proto, right] = raw_url.split("//", 1)
        [host, right] = right.split(":", 1)
        [port, right] = right.split("/", 1)
        [path, right] = right.split("?", 1)
        [query, fragment] = right.split("#", 1)
        pairs = [pair.split("=") for pair in query.split("&")]
        query = {key: val for [key, val] in pairs}
        return Url(proto, host, port, "/" + path, query, fragment)

    def hostpair(self) -> tuple[str, int]:
        return (self.host, self.port)

    def __str__(self) -> str:
        proto = self.scheme
        if proto[-1] != ":":
            proto += ":"
        port = self.port
        if port[0] != ":":
            port = f":{port}"
        if str(self.port) == "80" and (proto == "http:" or proto == "ws:"):
            port = ""
        if str(self.port) == "443" and (proto == "https:" or proto == "wss:"):
            port = ""
        query = ""
        if self.query != {}:
            query = "?" + "&".join([f"{key}={val}" for (key, val) in query.items])
        fragment = self.fragment
        if fragment != "" and fragment[0] != "#":
            fragment = f"#{fragment}"

        return f"{proto}//{self.host}{port}{self.path}{query}{fragment}"
