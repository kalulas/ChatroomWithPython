import socket
import threading

Host = '127.0.0.1'
Port = 58525


class Server:
    def __init__(self):
        """
        构造
        """
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__connections = list()
        self.__nicknames = list()
        self.__count = 0
        self.__upper_limit = 1

    def received_message(self, count):
        print("User " + self.__nicknames[count] + " has joined the chatroom")
        connection = self.__connections[count]
        while True:
            try:
                data = connection.recv(1024).decode()
                if data.startswith('1'):
                    print(data[1:])
                    # TODO nickname + '@' + data[1:] broadcast
            # abortion
            except ConnectionResetError:
                print("User " + self.__nicknames[count] + ' leaves accidentally')
                self.__count -= 1
                connection.close()
                break

    def start(self):
        self.__socket.bind((Host, Port))
        self.__socket.listen(5)
        print('[Server] Chatroom\'s ready')
        while True:
            try:

                conn, addr = self.__socket.accept()
                # detect whether room is full
                if self.__count < self.__upper_limit:
                    print('[Server] New Connection Accepted: ', conn.getsockname(), conn.fileno())
                    data = str(conn.recv(1024).decode())
                    if data.startswith('0'):
                        # User has send login message and login succeed
                        conn.send('0'.encode())
                        self.__connections.append(conn)
                        self.__nicknames.append(data[1:])
                        thread = threading.Thread(target=self.received_message, args=(self.__count,))
                        thread.setDaemon(True)
                        thread.start()
                        self.__count += 1
                else:
                    conn.send('9'.encode())
                    conn.close()
                    raise ValueError("Too Many Users")
            except ConnectionError:
                print("Connection Error")
            except ValueError:
                print("Too Many Users")


server = Server()
server.start()
