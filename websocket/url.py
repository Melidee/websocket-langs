from typing import Optional


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
    def parse(raw_url: str) -> "Url":
        """
        Parses a URL from a string

        Returns:
            Self | None: A `Url` object if parsing is successful, or `None` if parsing fails
        """
        scheme, host, port, path, fragment = [""] * 5
        query = {}
        if "://" in raw_url:
            [scheme, right] = raw_url.split("://", 1)
        if ":" in right:
            [host, right] = right.split(":", 1)
        if "/" in right:
            [port, right] = right.split("/", 1)
        elif right != "":
            port = right
        if "?" in right:
            [path, right] = right.split("?", 1)
        if "#" in right:
            [query_raw, fragment] = right.split("#", 1)
            pairs = [pair.split("=") for pair in query_raw.split("&")]
            query = {key: val for [key, val] in pairs}
        if port == "" and (scheme == "http" or scheme == "ws"):
            port = "80"
        if port == "" and (scheme == "https" or scheme == "wss"):
            port = "443"
        return Url(scheme, host, port, "/" + path, query, fragment)

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
            query = "?" + "&".join(
                [f"{key}={val}" for (key, val) in self.query.items()]
            )
        fragment = self.fragment
        if fragment != "" and fragment[0] != "#":
            fragment = f"#{fragment}"
        return f"{scheme}//{self.host}{port}{self.path}{query}{fragment}"

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Url)
            and self.scheme == other.scheme
            and self.host == other.scheme
            and self.port == other.port
            and self.path == other.path
            and self.query == other.query
            and self.fragment == other.fragment
        )
