from websocket.url import Url

def test_url_parses_all_parts():
    url = "scheme://host:1234/path?key=value#fragment"
    parsed = Url.parse(url)
    expected = Url("scheme", "host", "1234", "/path", {"key": "value"}, "fragment")
    assert parsed == expected

def test_parses_no_scheme():
    url = "host:1234/path?key=value#fragment"
    parsed = Url.parse(url)
    expected = Url("", "host", "1234", "/path", {"key": "value"}, "fragment")
    assert parsed == expected

def test_parses_no_host():
    url = "/path?key=value#fragment"
    parsed = Url.parse(url)
    expected = Url("scheme", "", "", "/path", {"key": "value"}, "fragment")
    assert parsed == expected

def test_parses_no_port():
    url = "scheme://host/path?key=value#fragment"
    parsed = Url.parse(url)
    expected = Url("scheme", "host", "", "/path", {"key": "value"}, "fragment")
    assert parsed == expected

def test_parses_no_path():
    url = "scheme://host:1234?key=value#fragment"
    parsed = Url.parse(url)
    expected = Url("scheme", "host", "1234", "", {"key": "value"}, "fragment")
    assert parsed == expected

def test_parses_no_query():
    url = "scheme://host:1234/path#fragment"
    parsed = Url.parse(url)
    expected = Url("scheme", "host", "1234", "/path", {"key": "value"}, "fragment")
    assert parsed == expected

def test_parses_no_fragment():
    url = "scheme://host:1234/path?key=value"
    parsed = Url.parse(url)
    expected = Url("scheme", "host", "1234", "/path", {"key": "value"}, "fragment")
    assert parsed == expected

def test_parses_host_only():
    url = "example.com"
    parsed = Url.parse(url)
    expected = Url("", "example.com", "")
    assert parsed == expected
