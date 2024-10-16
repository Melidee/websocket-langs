#!/bin/python3

from websocket import WebSocket

def main():
    with WebSocket.connect(("127.0.0.1", 8080)) as ws:
        while True:
            msg = input("> ")
            if msg == "exit":
                return
            ws.send_text(msg)
            print(ws.recv_text())

if __name__ == '__main__':
    main()