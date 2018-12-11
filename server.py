import socket
import threading

Host = '127.0.0.1'
Port = 58525

login = '0'
broadcast = '1'
exit = '8'
full = 'F'
existed = 'E'


class Server:
    def __init__(self):
        """
        构造
        """
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__user_dict = dict()
        # self.__count = 0
        self.__upper_limit = 5

    def broadcast(self, message):
        sender = message[1:9]
        # print(message)
        for user, conn in self.__user_dict.items():
            if user != sender:
                conn.send((broadcast + message[1:]).encode())

    def system_announce(self, message):
        sender = message[1:9]
        op_code = message[0]
        for user, conn in self.__user_dict.items():
            if user != sender:
                conn.send((op_code + message[1:]).encode())

    def received_message(self, user_name):
        print("User " + user_name + "has joined the chat")
        connection = self.__user_dict[user_name]
        while True:
            try:
                data = connection.recv(1024).decode()
                if data.startswith(broadcast):
                    self.broadcast(data)
                elif data.startswith(exit):
                    del self.__user_dict[user_name]
                    connection.close()
                    self.system_announce(data)
                    print("User " + user_name + 'has left the chat')
                    break
            # abortion
            except ConnectionResetError:
                print("User " + user_name + 'left the chat accidentally')
                self.system_announce(exit + user_name)
                del self.__user_dict[user_name]
                connection.close()
                break

    def start(self):
        self.__socket.bind((Host, Port))
        self.__socket.listen(5)
        print('[Server] Chatroom\'s Ready')
        while True:
            try:
                conn, addr = self.__socket.accept()
                # detect whether room is full
                if len(self.__user_dict) < self.__upper_limit:
                    print('[Server] New Connection Accepted: ', conn.getsockname(), conn.fileno())
                    data = str(conn.recv(1024).decode())
                    if data.startswith(login):
                        login_name = data[1:]
                        # user trying to register with an existed name
                        if login_name in self.__user_dict.keys():
                            conn.send((existed + 'Server  ').encode())
                            conn.close()
                            raise ValueError("User Requested an Existed Name")
                        # User has send login message and login succeed
                        conn.send((login + 'Server  ').encode())
                        self.system_announce(data)
                        self.__user_dict[login_name] = conn
                        thread = threading.Thread(target=self.received_message, args=(login_name,))
                        thread.setDaemon(True)
                        thread.start()
                else:
                    conn.send((full + 'Server  ').encode())
                    conn.close()
                    raise ValueError("Chatroom Full")
            except ConnectionError:
                print("Connection Error")
            except ValueError as ve:
                print(ve)


server = Server()
server.start()
