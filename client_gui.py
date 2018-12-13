import socket
import threading
import tkinter as tk
import tkinter.scrolledtext as tkst

HOST = '127.0.0.1'
PORT = 58525

login = '0'
broadcast = '1'
secret = '2'
exit = '8'
full = 'F'
existed = 'E'
shutdown = 'X'


class Client(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.__nickname = 'USER'
        self.prompt = ''
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__login = False

        self.message_line = 0

        self.name = tk.StringVar()
        self.server = tk.StringVar()

        self.resizable(False, False)
        container = tk.Frame(self)
        container.pack(side='top', fill='both', expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        frame_name = LoginFrame.__name__
        frame = LoginFrame(container, self)
        self.frames[frame_name] = frame

        frame_name = ChattingFrame.__name__
        frame = ChattingFrame(container, self)
        self.frames[frame_name] = frame

        self.raise_frame("LoginFrame")

    def raise_frame(self, frame_name):
        for frame in self.frames.values():
            frame.grid_remove()
        frame = self.frames[frame_name]
        frame.grid(row=0, column=0, sticky='ewsn')
        frame.tkraise()

    def get_frame_by_name(self, frame_name):
        for frame in self.frames.values():
            if str(frame.__class__.__name__) == frame_name:
                return frame
        print(frame_name + "NOT FOUND!")
        return None

    def login(self, user_name):
        self.__nickname = str(user_name).ljust(8)
        self.prompt = '[@' + self.__nickname + ']> '
        try:
            self.__socket.connect((HOST, PORT))
            # if connection succeeds, send login message
            send_message = (login + self.__nickname).encode()
            self.__socket.sendall(send_message)
            data = self.__socket.recv(1024)
            if str(data.decode()).startswith(full):
                raise ValueError("[System]Chatroom Full")
            elif str(data.decode()).startswith(existed):
                raise ValueError("[System]Name Already Existed")
            elif str(data.decode()).startswith(login):
                self.__login = True
                message = data.decode()
                # just in case
                if message[1:9] != self.__nickname:
                    raise ValueError("[System]Server Went Wrong")
                self.raise_frame("ChattingFrame")
                display_message = "[System] Login Success, display command list with \"\help\" \n"
                self.get_frame_by_name('ChattingFrame').add_message(display_message, "Blue")
                # sent list of current users
                self.get_frame_by_name('ChattingFrame').update_user_window(message[9:])
                thread = threading.Thread(target=self.receive_message_thread)
                thread.setDaemon(True)
                thread.start()
        except ValueError as ve:
            self.get_frame_by_name('LoginFrame').add_message(ve)
            self.name.set("")
            self.__socket.close()
            self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def shut_down(self):
        self.__login = False
        self.__socket.close()
        self.destroy()

    def help_menu(self):
        message = "------------------------------------------------------\n" \
                  "        Instruction of Gryffindor Common Room         \n" \
                  "            (0)[\exit] to leave the chat              \n" \
                  "(1)[@Receiver(space)message] send to a specific person\n" \
                  "          (2)Double Click to get one's name           \n" \
                  "------------------------------------------------------\n"
        self.get_frame_by_name('ChattingFrame').add_message(message, "OrangeRed")

    def display_broadcast(self, message):
        sender = message[1:9]
        text = message[9:]
        self.get_frame_by_name("ChattingFrame").\
            add_message('[Public][@' + sender + ']> ' + text, "black")

    def display_secret(self, message):
        sender = message[1:9]
        text = message[9:]
        self.get_frame_by_name("ChattingFrame").\
            add_message('[Secret][@' + sender + ']> ' + text, "HotPink")

    def display_system_message(self, message):
        sender = message[1:9]
        if sender[7] is not ' ':
            sender = sender + ' '
        if message[0] == login:
            self.get_frame_by_name("ChattingFrame").\
                add_message("[System] " + sender + "has joined the chat\n", "blue")
        elif message[0] == exit:
            self.get_frame_by_name("ChattingFrame"). \
                add_message("[System] " + sender + "has left the chat\n", "blue")
        self.get_frame_by_name("ChattingFrame"). \
            update_user_window(message[9:])

    def receive_message_thread(self):
        while self.__login:
            try:
                data = self.__socket.recv(1024).decode()
                if str(data).startswith(login) or str(data).startswith(exit):
                    self.display_system_message(data)
                elif str(data).startswith(broadcast):
                    self.display_broadcast(data)
                elif str(data).startswith(secret):
                    self.display_secret(data)
                elif str(data).startswith(shutdown):
                    self.shutdown()
            except Exception:
                print("[Client] Connection Close")
                self.__login = False
                self.__socket.close()
                self.destroy()

    def send_message(self, message):
        send = False
        op_code = ""
        if str(message).startswith("\exit"):
            message = ""
            op_code = exit
        elif str(message).startswith("\help"):
            self.help_menu()
        elif str(message).startswith("@"):
            op_code = secret
            message = message[1:]
            send = True
        else:
            op_code = broadcast
            send = True

        if len(op_code):
            send_message = (op_code + self.__nickname + message).encode()
            self.__socket.sendall(send_message)
        if op_code == exit:
            self.__login = False
            self.__socket.close()
            self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.destroy()
        return send


class LoginFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.receive_message_window = tk.Label(self, text="Welcome To My Chatroom :)")
        self.receive_message_window['font'] = ('consolas', 9)
        self.receive_message_window.grid(row=1, columnspan=2, padx=5, sticky="nsew")

        tk.Label(self, text=" Your nickname :").grid(row=0, column=0, pady=10)
        entry_name = tk.Entry(self, textvariable=self.controller.name)
        entry_name.grid(row=0, column=1, ipadx=30, padx=15, pady=10)

        self.login_button = tk.Button(self, text="LOGIN", width=10, command=self.login)
        self.login_button.grid(row=2, columnspan=2, padx=10, pady=10)
        # self.logout_button = tk.Button(self, text="EXIT", width=10, command=self.logout)
        # self.logout_button.grid(row=2, column=1, padx=10, pady=10)

        entry_name.bind('<KeyRelease-Return>', self.login)
        self.login_button.bind('<Return>', self.login)
        # self.logout_button.bind('<Return>', self.logout)

    def login(self, event=None):
        user_name = self.controller.name.get(),
        if len(user_name[0]) > 8:
            self.add_message('[System] User Name Limit <= 8 characters')
            self.controller.name.set("")
            return
        elif str(user_name[0]).isspace() or len(user_name[0]) == 0:
            self.add_message('[System] User Name [ ] is not available')
            self.controller.name.set("")
            return

        self.controller.connecting_thread = threading.Thread(target=self.controller.login, args=user_name)
        self.controller.connecting_thread.setDaemon(True)
        self.controller.connecting_thread.start()

    # def logout(self, event=None):
    #    self.controller.__login = False
    #    self.controller.destroy()

    def add_message(self, new_message):
        self.receive_message_window["text"] = new_message


class ChattingFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.receive_message_window = tkst.ScrolledText(self, width=60, height=20, undo=True)
        self.receive_message_window['font'] = ('consolas', 12)
        self.receive_message_window.grid(row=1, column=0, padx=10, pady=0, sticky="nsew")

        self.type_message_window = tk.Text(self, width=40, height=5, undo=True)
        self.type_message_window['font'] = ('consolas', 12)
        self.type_message_window.grid(row=2, padx=10, pady=20, rowspan=2, sticky="nsew")

        title = "HOST: " + HOST + " / PORT:" + str(PORT)
        self.members = tk.Label(self, width=15, text=title)
        self.members['font'] = ('consolas', 9)
        self.members.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

        self.members = tk.Label(self, width=15, text="MEMBERS")
        self.members['font'] = ('consolas', 9)
        self.members.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")

        self.chatroom_member_window = tk.Listbox(self, width=15, height=5, selectmode="browse")
        self.chatroom_member_window['font'] = ('consolas', 12)
        self.chatroom_member_window.grid(row=1, column=1, padx=10, pady=0, sticky="nsew")

        self.send_button = tk.Button(self, text="SEND", width=10, bg="white", command=self.send_message_from__gui__button)
        self.send_button.grid(row=2, column=1, padx=10)

        self.logout_button = tk.Button(self, text="EXIT", width=10, bg="white", command=self.logout)
        self.logout_button.grid(row=3, column=1, padx=10)

        self.type_message_window.bind('<KeyRelease-Return>', self.send_message_from__gui)
        self.logout_button.bind('<Return>', self.logout)
        self.chatroom_member_window.bind('<Double-Button-1>', self.get_name_for_secret)

        # prevent receive_message_window from input
        self.receive_message_window.config(state=tk.DISABLED)

    def send_message_from__gui__button(self, event=None):
        try:
            message = self.type_message_window.get("1.0", tk.END + '-1c')
            if self.controller.send_message(message + '\n'):
                if str(message).startswith("@"):
                    self.add_message('[Secret]' + self.controller.prompt + message + '\n', "HotPink")
                else:
                    self.add_message('[You   ]' + self.controller.prompt + message + '\n', "CornflowerBlue")
            self.type_message_window.delete("1.0", tk.END)
        except Exception:
            print("\Exit command")

    def send_message_from__gui(self, event=None):
        try:
            message = self.type_message_window.get("1.0", tk.END + '-1c')
            if len(message) != 0 and message != '\n' and not str(message).isspace():
                if self.controller.send_message(message):
                    if str(message).startswith("@"):
                        self.add_message('[Secret]' + self.controller.prompt + message, "HotPink")
                    else:
                        self.add_message('[You   ]' + self.controller.prompt + message, "CornflowerBlue")
            self.type_message_window.delete("1.0", tk.END)
        except Exception:
            print("\Exit command")

    def logout(self, event=None):
        self.controller.__login = False
        self.controller.send_message("\exit")

    def add_message(self, new_message, color="black"):
        self.controller.message_line += 1
        temp = "tag_" + str(self.controller.message_line)
        self.receive_message_window.tag_config(temp, foreground=color)
        self.receive_message_window.config(state=tk.NORMAL)
        self.receive_message_window.insert(tk.END, new_message, temp)
        self.receive_message_window.config(state=tk.DISABLED)
        self.receive_message_window.see(tk.END)

    def update_user_window(self, users):
        names = [name for name in str(users).split(" ") if name != ""]
        self.chatroom_member_window['listvariable'] = tk.StringVar(value=names)

    def get_name_for_secret(self, event=None):
        receiver_name = self.chatroom_member_window.get(self.chatroom_member_window.curselection())
        self.type_message_window.insert(tk.END, '@' + receiver_name + ' ')


if __name__ == '__main__':
    client = Client()
    client.title("Gryffindor Common Room")
    client.iconbitmap('.\\chat.ico')
    client.mainloop()
