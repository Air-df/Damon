import threading
import re
import os
import time
import traceback
import redis
import itchat
import settings
import tornado.websocket
import json

from modules import users
import itchat
from itchat.content import *
from ws4py.client.threadedclient import WebSocketClient
from apscheduler.schedulers.background import BackgroundScheduler

chatrooms = ['@@0439bbb8f6e1c6638fd4d1d481ac985229c40528f84fe4a8e83638be6c560ace',
             '@@ab54a996b3271291478264f692186b2e507ab327c14bc0374b9156487fb0aa68']

robot_name = 'robot1'


class DummyClient(WebSocketClient):
    def opened(self):
        self.send(settings.make_info(robot_name, msg_type=1))
        print('opened')

    def closed(self, code, reason=None):
        print("Closed down", code, reason)

    def received_message(self, m):
        try:
            msg_dct = json.loads(str(m))
            group_id = msg_dct['group_id']
            msg = msg_dct['msg']
            itchat.send(msg, group_id)
        except:
            pass


def get_time():
    """
    unix时间转换 -- 微信使用
    :param num:
    :return: 日期
    """
    format = '%Y.%m.%d %H:%M:%S'
    value = time.localtime(int(time.time()))
    dt = time.strftime(format, value)
    return dt


ws = DummyClient(settings.websocket_host, protocols=['chat'])
ws.connect()


def ws_client():
    while 1:
        try:
            ws = DummyClient(settings.websocket_host, protocols=['chat'])
            ws.connect()
            return ws
        except:
            pass


def update_members():
    """
    监听群成员变化
    :return:
    """
    rooms = itchat.get_chatrooms()

    db = users.UserInfo().db
    user_name = list(db[settings.user_info_table].find({'robot_name': robot_name}, {'_id': 0, 'user_name': 1}))[0][
        'user_name']
    member_table = db[settings.member_ids_table.format(user_name)]

    for room in rooms:
        room_id = room['UserName']
        members = room['MemberList']
        member_now_ids = [info['UserName'] for info in members]
        member_exsits_ids = [member['member_id'] for member in
                             member_table.find({'group_id': room_id}, {'member_id': 1})]
        new_members_id = [member for member in member_now_ids if member not in member_exsits_ids]
        new_members_name = ','.join([info['NickName'] for info in members if info['UserName'] in new_members_id])
        new_member_info = [info for info in members if info['UserName'] in new_members_id]

        # print([new_members_name])

        for member in members:
            member_id = member['UserName']
            member_name = member['NickName']
            # print(member_id, user_name)
            member_table.update({'group_id': room_id, 'member_id': member_id}, {'$set': {'member_name': member_name}})
        # member_table.remove({'member_id': {'$nin': member_now_ids}, 'group_id': room_id})
        member_table.update({'member_id': {'$nin': member_now_ids}, 'group_id': room_id},
                            {'$set': {'quit_time': get_time()}})

        if new_members_id:
            event_welcome(user_name, new_members_name, room_id)

        for info in new_member_info:
            dct = {}
            dct['member_id'] = info['UserName']
            dct['member_name'] = info['NickName']
            dct['group_id'] = room_id
            dct['join_time'] = get_time()
            member_table.insert(dct)
            if os.path.isfile(settings.head_imgs_dir.format(info['UserName'])):
                continue
            itchat.get_head_img(userName=info['UserName'], chatroomUserName=room_id,
                                picDir=settings.head_imgs_dir.format(info['UserName']))


def event_job():
    print('监听中')
    scheduler = BackgroundScheduler()
    scheduler.start()

    def send_romms(job_id, groups_id, content):
        print('调度任务执行')
        job_table = users.UserInfo().db[settings.jobs_table]
        try:
            for group_id in groups_id:
                itchat.send_msg(content, group_id)

            # 更改任务状态--发送成功
            job_table.update({'job_id': job_id}, {'$set': {'status': 1}})
        except:
            pass
            # 更改任务状态--发送失败
            job_table.update({'job_id': job_id}, {'$set': {'status': 2}})

    redis_pool = redis.ConnectionPool(host=settings.redis_host, password=settings.redis_pwd)
    conn_redis = redis.Redis(connection_pool=redis_pool, password=settings.redis_pwd)
    psb = conn_redis.pubsub()
    psb.subscribe(robot_name)
    for info in psb.listen():
        if info['type'] == 'message':
            job = json.loads(info['data'].decode())

            job_id = job['job_id']
            groups_id = job['groups_id']
            year = time.localtime().tm_year
            month = job['send_month']
            day = job['send_day']
            hour = job['send_hour']
            minute = job['send_minute']
            content = job['content']
            print(type(job), job)

            scheduler.add_job(send_romms, 'date', run_date='{}-{}-{} {}:{}:00'.format(year, month, day, hour, minute),
                              args=(job_id, groups_id, content))


def event_welcome(user_name, new_member_names, chatroom_id):
    """
    群新成员欢迎
    :param user_name: 机器人绑定的用户id @。。。。。
    :param sender_id: 群新成员id @。。。。。
    :param chatroom_id: 群id @@。。。。。
    :return: none
    """
    group_table = users.UserInfo().db[settings.groups_table]
    welcome_info = list(group_table.find({'user_name': user_name, 'group_id': chatroom_id, 'switch': 'on'},
                                         {'welcome_words': 1, 'frequence': 1}))
    if not welcome_info:
        return
    welcome_info = welcome_info[0]
    welcome_words = welcome_info['welcome_words']
    welcome_frequence = int(welcome_info['frequence']) * 60  # 换算为秒

    conn_redis = redis.Redis(host=settings.redis_host, password=settings.redis_pwd, db=13)
    is_exists = conn_redis.exists(chatroom_id)
    if is_exists:
        return
    else:
        print(welcome_words)
        itchat.send_msg('@' + new_member_names + '\n' + welcome_words, chatroom_id)
        conn_redis.set(chatroom_id, 'send', ex=welcome_frequence)


def event_keywords(group_id, sender_name, content):
    """
    群聊内容关键词检测
    :param group_id:
    :param sender_name:
    :param content:
    :return:
    """
    group_table = users.UserInfo().db[settings.groups_table]
    keywords = list(group_table.find({'group_id': group_id}, {'_id': 0, 'keywords': 1}))
    if 'keywords' in keywords[0]:
        keywords = keywords[0]['keywords']
    else:
        return
    items = list(users.UserInfo().db[settings.auto_response_table].find({'group_id': group_id},
                                                                        {'_id': 0, 'keywords': 1, 'reply': 1}))

    for keyword in keywords:
        if keyword in content:
            for item in items:
                if keyword in item['keywords']:
                    itchat.send_msg('@{}\n{}'.format(sender_name, item['reply']), group_id)
                    break
            break


# isGroupChat=True表示为群聊消息
@itchat.msg_register([TEXT, SHARING], isGroupChat=True)
def group_reply_text(msg):
    # 消息来自于哪个群聊
    chatroom_id = msg['FromUserName']
    to_user_name = msg['ToUserName']
    if '@@' not in chatroom_id:
        return

    # 发送者的昵称
    username = msg['ActualNickName']
    # 当前群名称
    chatroom_name = msg['User']['NickName']
    # 发信人微信id
    sender_id = msg['ActualUserName']

    print(json.dumps(msg))
    print(chatroom_name, chatroom_id, to_user_name, sep='***********')

    obj = users.UserInfo()
    user_name = obj.table.find({'robot_name': robot_name}, {'_id': 0, 'user_name': 1})[0]['user_name']

    member_table = settings.member_ids_table.format(user_name)
    # sender_name = obj.db[member_table].find({'member_id': sender_id}, {'member_name': 1})[0]['member_name']
    sender_name = username

    msg_type = 1
    if msg['Type'] == TEXT:
        content = msg['Content']
    elif msg['Type'] == 'Picture':
        msg_type = 2

    #############敏感词判断#####################

    #############敏感词判断#####################

    elif msg['AppMsgType'] == 5:
        msg_type = 3
        # 判断是否开启链接监测
        switch = 'on'
        if switch == 'on':
            print('分享链接')
            return
    elif msg['AppMsgType'] == 33:
        msg_type = 4
        # 判断是否开启小程序监测
        switch = 'on'
        if switch == 'on':
            print('小程序类型')
            return

    # 根据消息类型转发至其他群
    if msg['Type'] == TEXT:
        info_dct = settings.make_info(robot_name, to_user=user_name, msg=content, msg_type=2, is_success=0,
                                      sender_id=sender_id, sender_name=sender_name, group_id=chatroom_id)
        try:
            ws.send(info_dct)
        except:
            pass
        # itchat.send('%s' % (content), chatroom_id)

    # 保存聊天记录
    obj.db[settings.dialogue_history_table.format(user_name)].create_index('send_time')
    obj.db[settings.dialogue_history_table.format(user_name)].insert(
        {
            'user_name': user_name,
            'group_name': chatroom_name,
            'sender_name': sender_name,
            'group_id': chatroom_id,
            'sender_id': sender_id,
            'content': content,
            'msg_type': msg_type,
            'send_time': get_time(),
            'timestamp': int(time.time())
        }
    )

    # 更新群成员头像、昵称信息
    member_list = msg['User']['MemberList']
    member_info_list = []
    for member in member_list:
        dct = {}
        dct['member_id'] = member['UserName']
        dct['member_name'] = member['NickName']
        dct['group_id'] = chatroom_id
        member_info_list.append(dct)

    member_exists_ids = [info_dict['member_id'] for info_dict in
                         obj.db[member_table].find({'group_id': chatroom_id}, {'_id': 0, 'member_id': 1})]
    update_info = [info for info in member_info_list if info['member_id'] not in member_exists_ids]

    for info in update_info:
        obj.db[member_table].insert(info)
        if os.path.isfile(settings.head_imgs_dir.format(info['member_id'])):
            continue
        itchat.get_head_img(userName=info['member_id'], chatroomUserName=chatroom_id,
                            picDir=settings.head_imgs_dir.format(info['member_id']))

    # 更新用户绑定的群信息
    table = obj.db[settings.groups_table]
    group_ids = [item['group_id'] for item in table.find({'user_name': user_name}, {'_id': 0, 'group_id': 1})]
    if chatroom_id not in group_ids:
        table.insert({
            'user_name': user_name,
            'group_name': chatroom_name,
            'group_id': chatroom_id,
            'link_existed_info': settings.link_existed_info,
            'switch_link': 'off',
            'pro_existed_info': settings.pro_existed_info,
            'switch_pro': 'off',
            'sensitive_word_exsited_info': settings.sensitive_word_exsited_info,
            'switch_sensitive_word': 'off'
        })

    # print(msg['Content'], msg['Type'], chatroom_id, sep='\n')

    # 列表不为空，则有新成员进入
    if update_info:
        new_member_names = ','.join([member['member_name'] for member in update_info])
        event_welcome(user_name, new_member_names, chatroom_id)

    event_keywords(chatroom_id, sender_name, content)


@itchat.msg_register([TEXT, SHARING, PICTURE, VOICE, VIDEO, RECORDING], isFriendChat=True)
def deal_with_personal_msg(msg):
    msg_type = msg['Type']
    content = msg['Content']

    if msg['AppMsgType'] == 5:

        print('分享')

    elif msg_type == 'Text':
        print('文字')

    elif msg_type == 'Picture':
        path = 'E://'
        msg['Text'](path + msg['FileName'])
        print('图片')

    elif msg['AppMsgType'] == 33:
        print('小程序')


# 自动通过加好友
@itchat.msg_register(itchat.content.FRIENDS)
def deal_with_friend(msg):
    # 验证码处理
    conn_redis = redis.Redis(host=settings.redis_host, password=settings.redis_pwd, db=13)
    dct = json.loads(conn_redis.get(robot_name).decode())
    captcha_num = dct['captcha_num']
    user_name = dct['user_name']
    add_friend_compile = re.compile(str(captcha_num))
    u_id = msg['RecommendInfo']['UserName']
    if add_friend_compile.search(msg['Content']) is not None:
        itchat.add_friend(**msg['Text'])  # 自动将新好友的消息录入，不需要重载通讯录

        # 调用websocket 发送 跳转命令
        info_dct = settings.make_info(robot_name, to_user=user_name, msg=u_id, msg_type=4, is_success=1)
        ws.send(info_dct)

        # 发送欢迎语
        itchat.send_msg('我是鲲鲲 \n喜欢唱\t跳\tRAP\t打篮球 ', msg['RecommendInfo']['UserName'])
        itchat.send_image('cxk.jpg', msg['RecommendInfo']['UserName'])

        # 添加助手成功--->更改用户表，添加小助手名称信息--->更改is_first参数---->创建相关对应表
        db = users.UserInfo()
        db.table.update({'user_name': user_name},
                        {'$set': {'robot_name': robot_name, 'is_first': 0, 'wechat_id': u_id}})


if __name__ == '__main__':
    try:
        itchat.auto_login(hotReload=True)
        # itchat.auto_login()
        schedular = BackgroundScheduler()
        schedular.start()
        schedular.add_job(update_members, 'interval', minutes=settings.update_member_frequence)
        threading.Thread(target=event_job).start()

        itchat.run()
    except Exception as e:
        traceback.print_exc()
