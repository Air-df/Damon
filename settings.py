import json
import os

# 服务器地址、端口
server_host = '127.0.0.1'     # 本地测试
# server_host = '121.41.74.40'

server_port = '8888'  # 本地测试
# server_port = '8889'

# mongo 设置
mongo_host = '114.55.242.115'

mongo_db = 'wechat_robot'

user_info_table = 'user_info'

groups_table = 'groups'

dialogue_history_table = '{}_dialogue_history'

member_ids_table = '{}member_ids'

auto_response_table = 'auto_response'

material_table = '{}_material_table'

jobs_table = '{}_jobs_table'

# redis 设置
redis_host = '121.41.74.40'

redis_pwd = 'W4096redis'

websocket_host = 'ws://{}:{}/socket'.format(server_host, server_port)

control_url = 'http://{}:{}/control'.format(server_host, server_port)

# 头像存储位置
head_imgs_dir = r'E:\wechat_robot_tornado\static\images\head_imgs\{}.jpg'
# head_imgs_dir = os.getcwd() + r'\static\images\head_imgs\{}.jpg'

# 聊天记录每次加载条数
dialogue_history_length = 6

# 成员刷新频次
update_member_frequence = 1

# 违规监测，默认提示
link_existed_info = '亲爱的用户，请不要在群内发送链接信息，若多次触发我们将通知群管理员将您请出群'
pro_existed_info = '亲爱的用户，请不要在群内发送小程序信息，若多次触发我们将通知群管理员将您请出群。'
sensitive_word_exsited_info = '亲爱的用户，您发送的信息包含敏感违禁信息。若多次触发我们将通知群管理员将您请出群。'

words_dict = {
    1: ['link_existed_info', 'switch_link'],
    2: ['pro_existed_info', 'switch_pro'],
    3: ['sensitive_word_exsited_info', 'switch_sensitive_words']
}


def make_info(from_user, to_user='', msg='', msg_type=2, is_success=0, group_id='', sender_id='', sender_name=''):
    """
    websocket 信息格式
    :param from_user: 发送人
    :param to_user:  接收人
    :param msg: 信息内容
    :param msg_type: 信息类别。包含三种：
    默认为聊天信息
    1、用户名信息( websocket 初次连接)
    2、聊天信息
    3、存档信息
    4、添加好友确认，跳转指令
    :return: json 信息
    """
    dct = {
        'from_user': from_user,
        'to_user': to_user,
        'msg': msg,
        'msg_type': msg_type,
        'is_success': is_success,
        'group_id': group_id,
        'sender_id': sender_id,
        'sender_name': sender_name
    }
    return json.dumps(dct)


if __name__ == '__main__':
    pass

    # import redis
    # conn_redis = redis.Redis(host=redis_host, password=redis_pwd, db=13)
    # conn_redis.set('test', 'test', ex=30)