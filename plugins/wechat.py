import itchat
import time


"""
抓包工具开启，无法启动
"""
# 发送群消息
def SentChatRoomsMsg(name, context):
    itchat.get_chatrooms(update=True)
    iRoom = itchat.search_chatrooms(name)
    for room in iRoom:
        if room['NickName'] == name:
            userName = room['UserName']
            break
    itchat.send_msg(context, userName)


def lc():
    print("hello hello!")


def ec():
    print("bye bye bye")


if __name__ == '__main__':
    itchat.auto_login(hotReload=True, loginCallback=lc, exitCallback=ec)
    num = 1
    itchat.run()
    # while 1:
    #     itchat.send('好玩不%d次' % num)
    #     num += 1
    #     time.sleep(3)
