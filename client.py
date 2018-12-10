import socket
import threading

HOST = '127.0.0.1'
PORT = 58525


class Client:
    def __init__(self):
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__nickname = "USER"
        self.__login = False

    def send_message_thread(self, message):
        send_message = (str(1) + message).encode()
        self.__socket.sendall(send_message)

    def receive_message_thread(self):
        # print("receive_message_thread")
        while True:
            data = self.__socket.recv(1024)
            # TODO analyze sender and their message
            if len(data):
                print('Received', repr(data))

    def menu(self):
        # TODO menu to exit
        print("not finished yet")

    def main_loop(self):
        while True:
            if self.__login:
                message = input(self.__nickname + " :")
                if message == "menu":
                    self.menu()
                else:
                    thread = threading.Thread(target=self.send_message_thread(message), args=(message,))
                    thread.setDaemon(True)
                    thread.start()
            else:
                print("Please login first!")
                self.__nickname = input("Your nickname:")
                self.login()

    def login(self):
        try:
            self.__socket.connect((HOST, PORT))
            # if connection succeeds, send login message
            send_message = (str(0) + self.__nickname).encode()
            self.__socket.sendall(send_message)
            data = self.__socket.recv(1024)
            if data.decode() == '9':
                raise ConnectionError('Login Failed')
            else:
                self.__login = True
                # enough space for current user, start receiving messages
                thread = threading.Thread(target=self.receive_message_thread)
                thread.setDaemon(True)
                thread.start()
        except ConnectionError:
            print("[Client] Login Failed: Too many users")


client = Client()
client.main_loop()


