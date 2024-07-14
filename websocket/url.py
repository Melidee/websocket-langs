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
        self.scheme: str = scheme
        self.host: str = host
        self.port: str = port
        self.path: str = path
        self.query: dict[str, str] = query
        self.fragment: str = fragment

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
        """
        Gives the host and port in a tuple, as required by functions like socket.bind((host, port))

        Returns:
            (str, int): The tuple hostpair
        """
        return (self.host, int(self.port.strip(":")))

    def __str__(self) -> str:
        """
        Formats parts into a url string
        """
        scheme = self.scheme.strip(":")
        port = self.port.strip(":")
        if str(self.port) == "80" and (scheme == "http" or scheme == "ws"):
            port = ""
        if str(self.port) == "443" and (scheme == "https" or scheme == "wss"):
            port = ""
        query = ""
        if self.query != {}:
            query = "?" + "&".join([f"{key}={val}" for (key, val) in query.items])
        fragment = self.fragment
        if fragment != "" and fragment[0] != "#":
            fragment = f"#{fragment}"
        return f"{scheme}//{self.host}{port}{self.path}{query}{fragment}"
