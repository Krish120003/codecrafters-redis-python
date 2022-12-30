import socket
from threading import Thread, Lock

RECV_BLOCK_SIZE = 1024

data = {}
data_lock = Lock()


def responder(socket):
    global data
    while payload := socket.recv(RECV_BLOCK_SIZE):

        payload = payload.decode("utf-8").strip().split("\r\n")[1::][1::2]
        command = payload[0]
        if command == "echo":
            socket.send(f"+{' '.join(payload[1:])}\r\n".encode("utf-8"))
        elif command == "set":
            # we should lock the data here
            data_lock.acquire()
            key = payload[1]
            value = payload[2]
            data[key] = value
            # now we are done with the data, we can release the lock
            data_lock.release()
            socket.send(f"+OK\r\n".encode("utf-8"))
        elif command == "get":
            key = payload[1]
            # we should lock the data here
            data_lock.acquire()
            if key in data:
                value = data[key]
                # now we are done with the data, we can release the lock
                data_lock.release()
                socket.send(
                    (f"${len(value)}\r\n" +
                     value + "\r\n").encode("utf-8")
                )
            else:
                data_lock.release()
                socket.send(b"$-1\r\n")
        else:
            print(payload)
            socket.send(b"+PONG\r\n")


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)

    client_sockets = []

    # s = server_socket.accept()  # wait for client

    # while payload := s[0].recv(1024):  # recieve 1024 bytes
    #     s[0].send(b"+PONG\r\n")

    while True:
        conn = server_socket.accept()  # wait for client(s)
        if conn:
            print("Connecting to", conn)

            # start a thread to deal with the connection
            thread = Thread(target=responder, args=(conn[0],), daemon=True)
            thread.start()


if __name__ == "__main__":
    main()
