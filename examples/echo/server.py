#!/bin/python3.12

from websocket import WebSocketServer

port = 8080

def main():
    with WebSocketServer(("127.0.0.1", port)) as server:
        print(f"Server open on port 8080")
        while True:
            ws = server.accept()
            print(f"Connected to client")
            while True:
                msg = ws.recv_text()
                ws.send_text(msg)
    

if __name__ == '__main__':
    try:
        main()
    except OSError:
        main()