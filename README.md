## 计算机网络 Project 设计文档

Design Document for Computer Network Project

16307130116 陈柏铭



### 概述

本次project实现了基于SocketAPI的聊天室应用，提交文件夹目录下各文件分别为：

- /.idea pycharm相关
- .gitattributes & .gitignore git版本管理相关
- chat.ico 聊天室客户端UI图标
- client.py 客户端程序（早期命令行版本
- client_gui.py 客户端程序（后期GUI版本
- README.md git版本管理相关 有一些工作记录
- server.py 服务端程序

下面介绍协议设计以及聊天室功能设计



### 协议设计

客户端向服务端发送的数据格式：

| 操作码 1byte | 发送源 8bytes | 内容              | 备注                 |
| ------------ | ------------- | ----------------- | -------------------- |
| 0            | 用户名        | null              | 尝试以注册用户名登陆 |
| 1            | 用户名        | 聊天信息          | 发送聊天内容         |
| 2            | 用户名        | 接受者 + 发送信息 | 向接受者发送私聊     |
| 8            | 用户名        | null              | 退出聊天室           |

服务端向客户端发送的数据格式：

| 操作码 1byte | 发送源 8bytes     | 内容                 | 备注                        |
| ------------ | ----------------- | -------------------- | --------------------------- |
| 0            | 登陆用户          | 当前用户名，空格隔开 | 确认用户登陆，更新用户视窗* |
| 1            | 信息源用户/Server | 信息                 | 发送广播聊天/系统通知内容   |
| 2            | 私聊信息源用户    | 信息                 | 私聊 ， 发送给指定用户      |
| 8            | 退出用户          | null                 | 广播通知                    |
| F            | 服务器            |                      | 登陆反馈：聊天室满员        |
| E            | 服务器            |                      | 登陆反馈：当前用户名已存在  |
| X            | 服务器            |                      | 保险机制：通知用户关闭连接  |

**用户视窗：应用中可以看到当前在线人员的视窗*



**头部域设计细节：**

操作码（1byte）：用于标识确认操作的类型，可以将长度设计的更短，但为了让部分指令更易理解且取操作数更为方便所以设计为一个直接。

发送源（8bytes）：标识发送数据的操作者，为用户名或者系统标志。

内容（不定长）：用于存放其他信息，由于之后没有其他字段，所以不设置确定长度。



### 功能设计

下面根据用户从登陆到退出的过程介绍数据是如何被发送，处理（服务端），接收，处理（客户端）的。

#### 登陆

![blank](https://github.com/KaLuLas/ChatroomWithPython/blob/master/DesignDoc.assets/blank.gif?raw=true)

![toolong](https://github.com/KaLuLas/ChatroomWithPython/blob/master/DesignDoc.assets/toolong.gif?raw=true)

![NameExisted](https://github.com/KaLuLas/ChatroomWithPython/blob/master/DesignDoc.assets/NameExisted.gif?raw=true)



用户发送数据：0 + 用户名 -> 

服务端接收数据，检查聊天室是否满员，用户名是否存在：

1. 若聊天室满员：返回 F + 服务器标识 -> 用户收到聊天室满员提示

2. 若用户名存在：返回 E+ 服务器标识 -> 用户收到重复命名提示

3. 若成功登陆，服务端发送给全体：0 + 登陆用户 + 当前用户名列表（以空格隔开），登陆的用户会在聊天窗口上收到系统欢迎，而其他已登陆用户会收到用户登陆提示，所有用户都会根据用户名列表来更新窗体



#### 窗体更新

```python
    def update_user_window(self, users):
        names = [name for name in str(users).split(" ") if name != ""]
        self.chatroom_member_window['listvariable'] = tk.StringVar(value=names)
```

**新用户登陆时**

在用户登陆时，服务器收到用户发送的数据。若用户成功登陆，则服务端添加新连接之后，通过保存的{用户，连接}的键值（会在下文解释）向全聊天室发送当前聊天时的全部成员，数据格式为：0 + 登陆用户 + 当前用户名列表（以空格隔开）。接收用户根据上述情况进行不同的输出。

**用户退出时**

当用户退出时，服务器先从字典中将对应项删除，之后关闭连接，向剩余的所有连接发送当前的聊天室成员情况。数据格式为： 8 + 登出用户 + 当前用户名列表。接收用户进行输出与用户窗体更新。



#### 广播信息

![SendMessage](https://github.com/KaLuLas/ChatroomWithPython/blob/master/DesignDoc.assets/SendMessage.gif?raw=true)

用户发送数据：1 + 用户名 + 聊天信息 ->

服务端接收数据，将该数据通过所有用户名不等于发送用户的连接发送出去 ->

其他用户接收到数据：1 + 用户名 + 聊天信息， 将数据以“ [用户名] 聊天信息 ”的形式打印出来



#### 发送私聊

![secret](https://github.com/KaLuLas/ChatroomWithPython/blob/master/DesignDoc.assets/secret.gif?raw=true)

![SecretFail](https://github.com/KaLuLas/ChatroomWithPython/blob/master/DesignDoc.assets/SecretFail.gif?raw=true)

用户发送私聊：2 + 接收者 + 聊天信息 ->

服务端接收数据，检查接收者是否存在，

1. 若接收者存在，服务端将信息转发给该用户，形式：2 + 发送者 + 聊天信息
2. 若不存在，服务端以私聊形式发送给发起私聊用户， 形式：2 + 系统 + 错误信息

用户收到私聊信息后按照一般广播信息处理即可（在项目中做的特殊处理为前缀特殊和颜色特殊



#### 用户退出

用户发送数据：8 + 用户名 ->

服务器接收数据，删除对应键值对并关闭连接。与此同时用户聊天窗口已关闭。



### 细节设计

上述内容以外的设计，在代码中有体现。考虑到代码过长不适合全部贴出，下面结合部分代码进行介绍。



**用户名输入检测**

```python
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
```

出于特定的考量，用户名不应该是全空或者超出八个字节限制，因此在用户端对输入进行检测

若用户的输入不满足条件，则清空输入栏并在label中显示相应提示



**用户登陆**

```python
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
```

对提出登陆申请的用户进行聊天室现状检查，用户名检查，如功能设计->登陆部分所述。这里若连接建立成功，则为用户发送聊天室成员信息并开启一个新线程用于接收用户发送的数据，同样的在客户端也开启了一个线程用于接收服务端发送的数据，这里就不进行赘述。可以看到对各种异常情况都做了异常处理工作。



**用户帮助菜单**

```python
 def help_menu(self):
        message = "------------------------------------------------------\n" \
                  "        Instruction of Gryffindor Common Room         \n" \
                  "            (0)[\exit] to leave the chat              \n" \
                  "(1)[@Receiver(space)message] send to a specific person\n" \
                  "          (2)Double Click to get one's name           \n" \
                  "------------------------------------------------------\n"
        self.get_frame_by_name('ChattingFrame').add_message(message, "OrangeRed")
```

聊天室中的用户通过“\help”指令可呼出帮助菜单，可以看到用户可以用不同的操作和指令来执行功能



**输出信息区分**

```python
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
```

为了帮助用户更好辨别不同的信息类型，除了前缀区分还进行了颜色区分，在该聊天室应用中，个人发送信息，广播信息，私聊信息，系统信息，帮助菜单，以及用户登录登出信息各有不同的颜色。



**快速发送私聊功能**

![PrivateShortCut](https://github.com/KaLuLas/ChatroomWithPython/blob/master/DesignDoc.assets/PrivateShortCut.gif?raw=true)

```python
	self.type_message_window.bind('<KeyRelease-Return>', self.send_message_from__gui)
    
    def get_name_for_secret(self, event=None):
        receiver_name = self.chatroom_member_window./
        	get(self.chatroom_member_window.curselection())
        self.type_message_window.insert(tk.END, '@' + receiver_name + ' ')
```

用户不仅可以通过视窗看得知聊天室当前情况，还能通过双击获得私聊前缀 @用户名 ，由此可以便捷地发送私聊



**输入内容管控**

```python
    def send_message_from__gui(self, event=None):
        try:
            message = self.type_message_window.get("1.0", tk.END + '-1c')
            if len(message) != 0 and message != '\n' and not str(message).isspace():
                if self.controller.send_message(message):
                    if str(message).startswith("@"):
                        self.add_message('[Secret]' + \
                             self.controller.prompt + message, "HotPink")
                    else:
                        self.add_message('[You   ]' + \
                             self.controller.prompt + message, "CornflowerBlue")
            self.type_message_window.delete("1.0", tk.END)
        except Exception:
            print("\Exit command")
```

用户发送的内容不应该是无意义的空格或是回车，这个限制也一定程度解决了刷屏问题



### 放弃的设计

在项目中期曾构想过实现一个在聊天室中创建小型团队聊天的功能，并且基本实现了指令和数据处理方式。但由于预想操作过于繁琐，朴素GUI也不能提供直观的视觉效果，影响使用体验，并没有将这个功能实装。下面贴上对这个功能的一些设计构想。

**群组（预想）客户端向服务端发送 **

| 操作码 1byte | 发送源 8bytes |       内容        |     备注     |
| :----------: | :-----------: | :---------------: | :----------: |
|      3       |    用户名     | 群组名 + 发送信息 |   发送组聊   |
|      7       |    用户名     |      群组名       |   退出群组   |
|      G       |    用户名     | 组团用户 空格隔开 | 群组申请发送 |
|      A       |    用户名     |      群组名       | 接收群组申请 |

**1群组申请发送**

发送者输入：\group UserA UserB UserC …

自输出：组队请求发送

数据发送：G + User + 1 + 2 + …



**2接收到群组申请**

数据接收：A + Sender + Group name

处理：将group name 加入到记录中

自输出：Sender 邀请您 加入 groupname



**3同意群组申请**

发送者输入：\accept Group name

处理：检查groupname是否在其中（需要不存在组名确认

自输出：同意了Group name队伍请求

数据发送：A + User + Group name



**4进入群组通知**

数据接收： 0 + Sytem + Group name check

自输出：成功进入 Group name



**5群组信息发送**

发送者输入：>groupname message 

自输出显示\[groupx\]\[User\]message

数据发送：3 + User + Group name + message



**6群组信息发送**

数据接收： 3 + Sender + Group name + message

自输出显示\[groupx\]\[Sender\]message



**7退出群组（无须请求**

发送者输入：\exitgroup groupname

数据发送： 7 + User + groupname



**群组（预想）服务端向客户端发送**

| 操作码 1byte |  发送源 8bytes   |       内容       |        备注        |
| :----------: | :--------------: | :--------------: | :----------------: |
|      3       |     发送用户     |       信息       | 转发用户的组聊信息 |
|      A       | 组团申请发起用户 | 群组名（自生成） |   向用户发送申请   |

**1群组申请接收**

数据接收：G UserA UserB UserC …

处理： 对USERA USERB 发送群组申请

数据发送： A + Sender + Group name



**2收到加入群组确认**

数据接收：A + User + Group name

处理：在群组字典中确认加入对应成员用户名

数据发送：（对User）  0 + System + Group name check



**3群组信息转发**

数据接收：3 + sender + groupname + message

处理：对群组字典中非本人用户发送message

数据发送： 3 + sender + message



**4退出信息接收**

数据接收：7 + User + groupname

处理：从群组字典[groupname]中删掉user



### 收尾

很高兴能有这么一次机会能够实现一个自己的聊天室，虽然时间不算太长，但在协议和功能设计的工作上我也投入了不少热情 。在这次的大作业完成过程中，我有这么几项收获：一是认识到了命令行程序设计到GUI程序设计并不是一个继承的过程，所以初期想把命令行版本“加强”成GUI版本是很不切实际的；二是学会了如何设计根据协议进行数据传输处理的程序，上文中的群组功能虽然没有实现，确实我第一个按照一定工序进行设计的功能，体现出来效果明了，知道该按照什么顺序去做，也知道工作量会有多大；三是认识到了生活中看似简单的程序背后也有许多精妙的设计，若有机会我会很希望能够把这个应用完善到早期QQ那样的水平。

那么本次计算机网络设计文档就到此告一段落。

——2018/12/14

沦为smartgit测试仓库

——2020/11/29