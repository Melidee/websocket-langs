package wsgo

import (
	"bufio"
	"fmt"
	"io"
	"net"
	"net/http"
	"net/url"
	"strings"
)

const (
	secWSKey = "Sec-WebSocket-Key"
	secWSAccept = "Sec-WebSocket-Key"
	secWSVersion = "Sec-WebSocket-Version"
)

type Conn struct {
	conn     net.Conn
	isServer bool
}

func Connect(address string) (*Conn, error) {
	url, err := url.Parse(address)
	if err != nil {
		return nil, err
	}
	conn, err := net.Dial("tcp", address)
	if err != nil {
		return nil, err
	}
	req := http.Request{
		Method:     "GET",
		URL:        url,
		ProtoMajor: 1,
		ProtoMinor: 1,
		Header:     http.Header{
			"Connection": {"Upgrade"},
			"Upgrade": {"websocket"},
			"Sec-WebSocket-Key": {newSecWSKey()},
			"Sec-WebSocket-Version": {"13"},
		},
		Body:       io.NopCloser(strings.NewReader("")),
	}
	err = req.Write(conn)
	if err != nil {
		return nil, err
	}
	res, err := http.ReadResponse(bufio.NewReader(conn), &req)
	if err != nil {
		return nil, err
	}
	if !isValidWSResponse(res) {
		return nil, fmt.Errorf("recieved invalid response from websocket server")
	}
	return &Conn{conn, false}, nil
}

func isValidWSResponse(res *http.Response) bool {
	return res.ProtoAtLeast(1, 1) && 
		res.Status == http.StatusText(http.StatusSwitchingProtocols) && 
		res.Header.Get("Upgrade") == "websocket" &&
		res.Header.Get("Connection") == "Upgrade" &&
		res.Header.Get(secWSAccept) == makeSecWSAccept(res.Header.Get(secWSKey))
}

func newSecWSKey() string {
	return ""
}

func makeSecWSAccept(string) string {
	return ""
}

type Frame struct {
	fin bool
	opcode uint8
	payloadLen uint64
	mask [4]byte
	payload []byte
}

func deserializeFrame(data []byte) *Frame {
	
	fin := data[0] & 0b1000_0000 == 0b1000_0000
	opcode := data[0] & 0b1111
	isMasked := data[1] & 0b1000_0000 == 0b1000_0000
	payloadLen := data[1] & 0b0111_1111
	cursor := 2
	if len == 126 {

	} else if len == 127 {

	}
	return &Frame{
		fin,
		opcode,
	}
}