class Url:
    def __init__(
        self,
        proto: str,
        host: str,
        port: str,
        path: str = "",
        query: dict[str, str] = {},
        fragment: str = "",
    ) -> None:
        self.proto = proto
        self.host = host
        self.port = port
        self.path = path
        self.query = query
        self.fragment = fragment

    @staticmethod
    def parse(raw_url: str) -> "Url":
        [proto, rest] = raw_url.split("//", 1)
        [host, rest] = rest.split(":", 1)
        [port, rest] = rest.split("/", 1)
        [path, rest] = rest.split("?", 1)
        [query, fragment] = rest.split("#", 1)
        pairs = [pair.split("=") for pair in query.split("&")]
        query = {key: val for [key, val] in pairs}
        return Url(proto, host, port, "/" + path, query, fragment)

    def __str__(self) -> str:
        proto = self.proto
        if proto[-1] != ":":
            proto += ":"
        query = ""
        if self.query != {}:
            query = "?" + "&".join([f"{key}={val}" for (key, val) in query.items])
        fragment = self.fragment
        if fragment != "" and fragment[0] != "#":
            fragment = "#" + fragment
        return f"{proto}//{self.host}:{self.port}{self.path}{query}{fragment}"
