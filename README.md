## 格兰芬多的公共休息室

**计算机网络Project**



**客户端发向服务端套接字格式：**

| 操作码 1byte | 发送源 8bytes |       内容        |      备注      |
| :----------: | :-----------: | :---------------: | :------------: |
|      0       |    用户名     |       null        | 登陆注册用户名 |
|      1       |    用户名     |     聊天信息      |  发送聊天内容  |
|      2       |    用户名     | 接受者 + 发送信息 |    发送私聊    |
|              |               |                   |                |
|              |               |                   |                |
|              |               |                   |                |
|              |               |                   |                |
|      8       |    用户名     |       null        |   退出聊天室   |

**私聊** 

1发送私聊：

发送者输入：@Receiver Message 

自输出：[Secret] + 一般输出内容 color=HotPink

数据发送：2 +  Sender + Receiver + Message



2收到系统提示：（不存在用户名或指令错误）

数据接收：2 +  System + Message

处理：输出 [Secret] +  System + Message color=HotPink



3收到用户私信：

数据接收：2 +  Sender + Message

处理：输出 [Secret] +  Sender + Message color=HotPink

*要自己聊自己也是可以的



**群组（预想）**

| 操作码 1byte | 发送源 8bytes |       内容        |     备注     |
| :----------: | :-----------: | :---------------: | :----------: |
|      3       |    用户名     | 群组名 + 发送信息 |   发送组聊   |
|      7       |    用户名     |      群组名       |   退出群组   |
|      G       |    用户名     | 组团用户 空格隔开 | 群组申请发送 |
|      A       |    用户名     |      群组名       | 接收群组申请 |

1群组申请发送

发送者输入：\group UserA UserB UserC …

自输出：组队请求发送

数据发送：G + User + 1 + 2 + …



2接收到群组申请

数据接收：A + Sender + Group name

处理：将group name 加入到记录中

自输出：Sender 邀请您 加入 groupname



3同意群组申请

发送者输入：\accept Group name

处理：检查groupname是否在其中（需要不存在组名确认

自输出：同意了Group name队伍请求

数据发送：A + User + Group name



4进入群组通知

数据接收： 0 + Sytem + Group name check

自输出：成功进入 Group name



5群组信息发送

发送者输入：>groupname message 

自输出显示\[groupx\]\[User\]message

数据发送：3 + User + Group name + message



6群组信息发送

数据接收： 3 + Sender + Group name + message

自输出显示\[groupx\]\[Sender\]message



7退出群组（无须请求

发送者输入：\exitgroup groupname

数据发送： 7 + User + groupname







**服务端发向客户端套接字格式：**

| 操作码 1byte |  发送源 8bytes  | 内容 |         备注          |
| :----------: | :-------------: | :--: | :-------------------: |
|      0       |    登陆用户     | null |  确认登陆，广播通知   |
|      1       | 发送用户/Server | 信息 |   发送聊天/通知内容   |
|      2       |    发送用户     | 信息 | 私聊 / 发送给指定用户 |
|              |                 |      |                       |
|              |                 |      |                       |
|              |                 |      |                       |
|              |                 |      |                       |
|      8       |    退出用户     | null |       广播通知        |
|      F       |     服务器      |      |      聊天室满员       |
|      E       |     服务器      |      |   当前用户名已存在    |

**私聊** 

服务器：在用户名-连接字典中取出对应的连接进行发送

收到私信申请

数据接收：2 + Sender + Receiver + Message

处理：检查Receiver是否存在，存在转发给用户，不存在则发送错误通知

数据发送：

（对目标User）  2 + Sender + Message

or

（对源User） 2 + System + 错误信息



**群组（构想）**

| 操作码 1byte |  发送源 8bytes   |       内容       |        备注        |
| :----------: | :--------------: | :--------------: | :----------------: |
|      3       |     发送用户     |       信息       | 转发用户的组聊信息 |
|      A       | 组团申请发起用户 | 群组名（自生成） |   向用户发送申请   |
|              |                  |                  |                    |
|              |                  |                  |                    |
|              |                  |                  |                    |

1群组申请接收

数据接收：G UserA UserB UserC …

处理： 对USERA USERB 发送群组申请

数据发送： A + Sender + Group name



2收到加入群组确认

数据接收：A + User + Group name

处理：在群组字典中确认加入对应成员用户名

数据发送：（对User）  0 + System + Group name check



3群组信息转发

数据接收：3 + sender + groupname + message

处理：对群组字典中非本人用户发送message

数据发送： 3 + sender + message



4退出信息接收

数据接收：7 + User + groupname

处理：从群组字典[groupname]中删掉user



2018/12/11 非常艰辛地添加了GUI



**TODO：** 

1. 空白姓名问题 **finished**
2. \help 帮助菜单 **finished**
3. 双方语言框调整 **可能有长句，太丑。摸了**

4. 添加其他功能
5. 1. 私聊  **finished**/ 
   2. 群组 **过于繁琐aborted**/ 
   3. 在线成员 **视图**
   4. 通知 只是颜色不同 有空就做
6. GUI微调（一边有在调


