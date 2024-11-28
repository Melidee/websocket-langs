package wsgo

import (
	"bufio"
	"crypto/rand"
	"encoding/binary"
	"fmt"
	"io"
	"net"
	"net/http"
	"net/url"
	"strings"
	"unicode/utf8"
)

const (
	secWSKey     = "Sec-WebSocket-Key"
	secWSAccept  = "Sec-WebSocket-Key"
	secWSVersion = "Sec-WebSocket-Version"
)

type Conn struct {
	tcp        net.Conn
	isServer   bool
	address    string
	recvText   chan string
	recvBin    chan []byte
	byteStream chan byte
}

func newConn(tcp net.Conn, isServer bool, address string) *Conn {
	recvText := make(chan string)
	recvBin := make(chan []byte)
	byteStream := make(chan byte)
	conn := &Conn{
		tcp,
		isServer,
		address,
		recvText,
		recvBin,
		byteStream,
	}
	go connListen(conn, recvText, recvBin)
	return conn
}

func connListen(conn *Conn, recvText chan string, recvBin chan []byte) {
	buf := make([]byte, 4096)
	readFrame := func() *Frame {
		_ = buf
		return nil
	}
	for {
		frame := readFrame()
		if frame.opcode == opcodeContinue {

		} else if frame.opcode == opcodeText {
			if !utf8.Valid(frame.payload) {

			}
			text := string(frame.payload)
			recvText <- text
		} else if frame.opcode == opcodeBinary {
			recvBin <- frame.payload
		} else if frame.opcode == opcodeClose {

		} else if frame.opcode == opcodePing {
			conn.Pong()
		} else if frame.opcode == opcodePong {

		} else {
			conn.fail()
		}
	}
}

func Connect(address string) (*Conn, error) {
	url, err := url.Parse(address)
	if err != nil {
		return nil, err
	}
	tcp, err := net.Dial("tcp", address)
	if err != nil {
		return nil, err
	}
	req := http.Request{
		Method:     "GET",
		URL:        url,
		ProtoMajor: 1,
		ProtoMinor: 1,
		Header: http.Header{
			"Connection":            {"Upgrade"},
			"Upgrade":               {"websocket"},
			"Sec-WebSocket-Key":     {newSecWSKey()},
			"Sec-WebSocket-Version": {"13"},
		},
		Body: io.NopCloser(strings.NewReader("")),
	}
	err = req.Write(tcp)
	if err != nil {
		tcp.Close()
		return nil, err
	}
	res, err := http.ReadResponse(bufio.NewReader(tcp), &req)
	if err != nil {
		tcp.Close()
		return nil, err
	}
	if !isValidWSResponse(res) {
		tcp.Close()
		return nil, fmt.Errorf("recieved invalid response from websocket server")
	}
	return newConn(tcp, false, address), nil
}

func (conn *Conn) Ping() {

}

func (conn *Conn) Pong() {

}

func (conn *Conn) Close() {
	
}

func (conn *Conn) fail() {

}

type Listener struct {
	addr     string
	listener net.Listener
}

func Listen(addr string) (*Listener, error) {
	l, err := net.Listen("tcp", addr)
	if err != nil {
		return nil, err
	}
	return &Listener{
		addr,
		l,
	}, nil
}

func (l *Listener) Accept() (*Conn, error) {
	tcp, err := l.listener.Accept()
	if err != nil {
		tcp.Close()
		return nil, err
	}
	req, err := http.ReadRequest(bufio.NewReader(tcp))
	if err != nil {
		tcp.Close()
		return nil, err
	}
	if !isValidWSRequest(req) {
		tcp.Close()
		return nil, fmt.Errorf("recieved invalid opening request")
	}
	res := http.Response{
		Status:     http.StatusText(http.StatusSwitchingProtocols),
		StatusCode: http.StatusSwitchingProtocols,
		Proto:      "HTTP/1.1",
		Header: http.Header{
			"Upgrade":    {"websocket"},
			"Connection": {"Upgrade"},
			secWSAccept:  {makeSecWSAccept(req.Header.Get(secWSAccept))},
		},
	}
	res.Write(tcp)
	return newConn(tcp, true, l.addr), nil
}

func isValidWSRequest(req *http.Request) bool {
	return req.ProtoAtLeast(1, 1) &&
		req.Method == http.MethodGet &&
		req.Header.Get("Upgrade") == "websocket" &&
		req.Header.Get("Connection") == "Upgrade" &&
		req.Header.Get(secWSKey) != "" &&
		req.Header.Get("Host") == ""
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

const (
	opcodeContinue uint8 = 0x0
	opcodeText           = 0x1
	opcodeBinary         = 0x2
	opcodeClose          = 0x8
	opcodePing           = 0x9
	opcodePong           = 0xA
)

type Frame struct {
	fin        uint8
	opcode     uint8
	payloadLen uint64
	mask       []byte
	payload    []byte
}

func newFrame(opcode uint8, mask []byte, payload []byte) *Frame {
	return &Frame{
		fin:        0b1000_0000,
		opcode:     opcode,
		payloadLen: uint64(len(payload)),
		mask:       mask,
		payload:    payload,
	}
}

func deserializeFrame(data []byte) *Frame {
	fin := data[0] & 0b1000_0000
	opcode := data[0] & 0b1111
	isMasked := data[1]&0b1000_0000 == 0b1000_0000
	payloadLen := uint64(data[1] & 0b0111_1111)
	cursor := 2
	if payloadLen == 126 {
		payloadLen = binary.BigEndian.Uint64(data[cursor : cursor+2])
		cursor += 2
	} else if payloadLen == 127 {
		payloadLen = binary.BigEndian.Uint64(data[cursor : cursor+8])
		cursor += 8
	}
	var mask []byte
	if isMasked {
		mask = data[cursor : cursor+4]
		cursor += 4
	}
	payload := data[cursor : cursor+int(payloadLen)]
	return &Frame{
		fin,
		opcode,
		payloadLen,
		mask,
		payload,
	}
}

func (f Frame) serialize() []byte {
	maskByte := byte(0)
	if f.mask == nil {
		maskByte = byte(0b1000_0000)
	}
	lenByte := byte(f.payloadLen)
	var lenExt []byte
	if f.payloadLen > 65535 {
		binary.BigEndian.AppendUint64(lenExt, f.payloadLen)
		lenByte = 127
	} else if f.payloadLen > 125 {
		binary.BigEndian.AppendUint64(lenExt, f.payloadLen)
		lenByte = 126
	}
	serialized := []byte{f.fin | f.opcode, maskByte | lenByte}
	serialized = append(serialized, lenExt...)
	serialized = append(serialized, f.mask...)
	serialized = append(serialized, f.payload...)
	return serialized
}

func (f Frame) setFin(isFin bool) {
	if isFin {
		f.fin = 0b1000_0000
	} else {
		f.fin = 0
	}
}

func randomMask() []byte {
	mask := make([]byte, 4)
	rand.Read(mask)
	return mask
}
