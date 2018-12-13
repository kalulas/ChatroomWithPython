import socket
import threading

Host = '127.0.0.1'
Port = 58525

login = '0'
broadcast = '1'
secret = '2'
exit = '8'
full = 'F'
existed = 'E'
shutdown = 'X'


class Server:
    def __init__(self):
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__user_dict = dict()
        self.__upper_limit = 10

    def broadcast(self, message):
        sender = message[1:9]
        for user, conn in self.__user_dict.items():
            if user != sender:
                conn.send((broadcast + message[1:]).encode())

    def secret(self, message):
        sender = message[1:9]
        receiver_end_spot = str(message).find(" ", 9)
        receiver = str(message[9:receiver_end_spot]).ljust(8)
        if receiver in self.__user_dict.keys():
            conn = self.__user_dict[receiver]
            send_message = secret + sender + message[receiver_end_spot + 1:]
            conn.send(send_message.encode())
        else:
            conn = self.__user_dict[sender]
            conn.send((secret + "System  " + "No User Found or @Command Error\n").encode())

    # user exit announce only (for now 2018/12/13
    def system_announce(self, message):
        op_code = message[0]
        for user, conn in self.__user_dict.items():
            conn.send((op_code + message[1:]).encode())

    def update_user_window(self, message):
        op_code = message[0]
        for user, conn in self.__user_dict.items():
                conn.send((op_code + message[1:]).encode())

    def received_message(self, user_name):
        print("User " + user_name + "has joined the chat")
        connection = self.__user_dict[user_name]
        while True:
            try:
                data = connection.recv(1024).decode()
                if data.startswith(broadcast):
                    self.broadcast(data)
                elif data.startswith(secret):
                    self.secret(data)
                elif data.startswith(exit):
                    del self.__user_dict[user_name]
                    connection.close()
                    if len(self.__user_dict):
                        message = str(data) + " ".join(self.__user_dict.keys())
                        self.system_announce(message)
                    print("User " + user_name + 'has left the chat')
                    break
            # abortion
            except ConnectionResetError:
                print("User " + user_name + 'left the chat accidentally')
                del self.__user_dict[user_name]
                self.system_announce(exit + user_name)
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
                        self.__user_dict[login_name] = conn
                        users_list = " ".join(self.__user_dict.keys())
                        self.update_user_window(login + login_name + users_list)
                        thread = threading.Thread(target=self.received_message, args=(login_name,))
                        thread.setDaemon(True)
                        thread.start()
                else:
                    conn.send((full + 'Server  ').encode())
                    conn.close()
                    raise ValueError("Chatroom Full")
            except ConnectionError:
                for conn in self.__user_dict.values():
                    conn.send(shutdown.encode())
                    conn.close()
                self.__user_dict = {}
                print("Connection Error, Chatroom shut down")
            except ValueError as ve:
                print(ve)


server = Server()
server.start()
