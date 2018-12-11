import socket
import threading

HOST = '127.0.0.1'
PORT = 58525

login = '0'
broadcast = '1'
exit = '8'
full = 'F'
existed = 'E'


class Client:
    def __init__(self):
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__nickname = "USER"
        self.__login = False

    def display_broadcast(self, message):
        sender = message[1:9]
        text = message[9:]
        print(sender + ":" + text)

    def display_system_message(self, message):
        sender = message[1:9]
        if message[0] == login:
            print("[System] " + sender + "has joined the chat")
        elif message[0] == exit:
            print("[System] " + sender + "has left the chat")

    def send_message_thread(self, op_code, message):
        send_message = (op_code + self.__nickname + message).encode()
        self.__socket.sendall(send_message)

    def receive_message_thread(self):
        while True:
            try:
                data = self.__socket.recv(1024).decode()
                if str(data).startswith(login) or str(data).startswith(exit):
                    self.display_system_message(data)
                elif str(data).startswith(broadcast):
                    self.display_broadcast(data)
            except Exception:
                print("[Client] Connection Close")
                break

    def help_menu(self):
        # TODO help_menu to print message
        print("not finished yet")

    def main_loop(self):
        while True:
            if self.__login:
                op_code = ""
                message = input()

                if message == "\exit":
                    message = ""
                    op_code = exit
                elif message == "\help":
                    self.help_menu()
                else:
                    op_code = broadcast

                if len(op_code):
                    thread = threading.Thread(target=self.send_message_thread, args=(op_code, message,))
                    thread.setDaemon(True)
                    thread.start()

                if op_code == exit:
                    self.__login = False
                    self.__socket.close()
                    self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            else:
                print("[Client] Please login first")
                self.__nickname = input("[Client] Your nickname (<= 8 characters):").ljust(8, " ")
                if len(self.__nickname) > 8:
                    self.__nickname = ""
                    continue
                self.login()
                if self.__login:
                    print("[Client] Login Success, display command list with \"\help\" ")

    def login(self):
        try:
            self.__socket.connect((HOST, PORT))
            # if connection succeeds, send login message
            send_message = (login + self.__nickname).encode()
            self.__socket.sendall(send_message)
            data = self.__socket.recv(1024)
            if str(data.decode()).startswith(full):
                raise ValueError("Chatroom Full")
            elif str(data.decode()).startswith(existed):
                raise ValueError("Name Already Existed")
            elif str(data.decode()).startswith(login):
                self.__login = True
                # enough space for current user, start receiving messages
                thread = threading.Thread(target=self.receive_message_thread)
                thread.setDaemon(True)
                thread.start()
        except ValueError as ve:
            print(ve)
            self.__socket.close()
            self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


client = Client()
client.main_loop()


