from websocket import http
from websocket.http import Request
from websocket.url import Url


class TestRequest:
    def test_parses_trivial_request(self):
        req = "GET / HTTP/1.1\r\nHost: www.example.com\r\nContent-Length: 13\r\n\r\nHello, World!"
        parsed = Request.parse(req)
        reference = Request(
            "GET",
            "/",
            {"Host": "www.example.com", "Content-Length": "13"},
            "Hello, World!",
        )
        print(f"------ Parsed ------\n{parsed}\n----- Reference -----\n{reference}")
        assert parsed == reference

    def test_adds_content_length_header(self):
        req = "GET / HTTP/1.1\r\nHost: www.example.com\r\n\r\nHello, World!"
        parsed = Request.parse(req)
        assert parsed.headers.get("Content-Length") == "13"

    def test_should_reject_invalid_request_line(self):
        req = "WRONG GET / HTTP/1.1\r\n\r\n"
        try:
            _ = Request.parse(req)
            assert False
        except ValueError:
            assert True

    def test_should_reject_invalid_proto(self):
        req = "GET / HTTP/0.9\r\n\r\n"
        try:
            parsed = Request.parse(req)
            print(f"------ proto ------\n{parsed.proto}")
            assert False
        except ValueError:
            assert True

    def test_should_reject_invalid_header_format(self):
        req = "GET / HTTP/1.1\r\nHost hostname\r\n\r\n"
        try:
            parsed = Request.parse(req)
            print(parsed.headers)
            assert False
        except ValueError:
            assert True

    def test_ws_default_request_is_valid(self):
        url = Url("ws:", "example.com", "8080", "/chat")
        req = Request.new_ws(url)
        print(f"------ Request ------\n{req}")
        assert req.is_valid_ws_request()

    def test_ws_validator_requires_all_headers(self):
        url = Url("ws:", "example.com", "8080", "/chat")
        req = Request.new_ws(url)
        print(f"------ Request ------\n{req}")

        del req.headers["Host"]
        assert not req.is_valid_ws_request()
        req = Request.new_ws(url)

        del req.headers["Connection"]
        assert not req.is_valid_ws_request()
        req = Request.new_ws(url)

        del req.headers["Upgrade"]
        assert not req.is_valid_ws_request()
        req = Request.new_ws(url)

        del req.headers[http.HEADER_WS_KEY]
        assert not req.is_valid_ws_request()
        req = Request.new_ws(url)

        del req.headers[http.HEADER_WS_VERSION]
        assert not req.is_valid_ws_request()
        req = Request.new_ws(url)

    
