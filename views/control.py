import json
import hashlib
import tornado.web
import settings
import redis

from modules import users


def make_md5(words):
    hash = hashlib.md5()
    hash.update(words.encode(encoding='utf-8'))
    return hash.hexdigest()


class ControlHandler(tornado.web.RequestHandler):
    def get(self, user_name, *args, **kwargs):
        print(user_name)
        db = users.UserInfo().db[settings.groups_table]
        group_list = [x for x in db.find({'user_name': user_name}, {'_id': 0, 'group_name': 1, 'group_id': 1})]
        self.render('control.html', websocket_host=settings.websocket_host, group_list=group_list, user_name=user_name)

    def post(self, *args, **kwargs):
        group_id = self.get_argument('group_id')
        user_name = self.get_argument('user_name')
        db = users.UserInfo().db[settings.member_ids_table.format(user_name)]
        members = [x for x in db.find({'group_id': group_id, 'quit_time': {'$exists': False}},
                                      {'_id': 0, 'member_id': 1, 'member_name': 1})]
        self.write({'members': members})


class HistoryHandler(tornado.web.RequestHandler):
    """
    聊天记录获取
    """

    def post(self, *args, **kwargs):
        user_name = self.get_argument('user_name')
        group_id = self.get_argument('group_id')
        page_num = int(self.get_argument('page_num'))
        print('history handler')
        print(user_name, group_id, page_num)
        mongo_obj = users.UserInfo().db
        results = mongo_obj[settings.dialogue_history_table.format(user_name)].find(
            {'group_id': group_id},
            {'_id': 0, 'sender_name': 1, 'content': 1, 'send_time': 1, 'sender_id': 1}).sort(
            [('send_time', -1)]).limit(settings.dialogue_history_length).skip(
            (page_num - 1) * settings.dialogue_history_length)
        datas = [item for item in results]
        print(datas)
        self.write(json.dumps({'datas': datas}))


class GroupManager(tornado.web.RequestHandler):
    """
    群成员管理
    """

    def get(self, user_name, *args, **kwargs):
        self.render('manage_group.html', user_name=user_name)

    def post(self, *args, **kwargs):
        print('group_manager post')


class Welcome(tornado.web.RequestHandler):
    """
    入群欢迎语
    """

    def get(self, user_name, *args, **kwargs):
        mongo_obj = users.UserInfo().db
        groups = mongo_obj[settings.groups_table].find(
            {'user_name': user_name}, {'_id': 0, 'group_name': 1, 'group_id': 1}
        )
        welcome_words = list(mongo_obj[settings.groups_table].find(
            {'user_name': user_name, 'welcome_words': {'$exists': True}},
            {'_id': 0, 'group_name': 1, 'group_id': 1, 'welcome_words': 1}
        ))
        self.render('welcome.html',
                    user_name=user_name, groups=groups, server_host=settings.server_host,
                    server_port=settings.server_port, welcome_words=welcome_words)

    def post(self, user_name, *args, **kwargs):
        group_ids = self.get_argument('groups').split(',')
        welcome_words = self.get_argument('welcome_words')
        frequence = int(self.get_argument('frequence'))
        mongo_obj = users.UserInfo().db

        for group_id in group_ids:
            mongo_obj[settings.groups_table].update(
                {'group_id': group_id},
                {'$set': {'welcome_words': welcome_words, 'frequence': frequence, 'switch': 'on'}}
            )

        print(welcome_words)
        print(group_ids)
        self.write({'msg': 'success'})


class AutoResponse(tornado.web.RequestHandler):
    """
    自动回复
    """

    def get(self, user_name, *args, **kwargs):
        mongo_obj = users.UserInfo().db
        groups = mongo_obj[settings.groups_table].find(
            {'user_name': user_name}, {'_id': 0, 'group_name': 1, 'group_id': 1}
        )
        keywords = []
        self.render('auto_response.html', user_name=user_name, groups=groups, server_host=settings.server_host,
                    server_port=settings.server_port, keywords=keywords)

    def post(self, user_name, *args, **kwargs):
        group_ids = self.get_argument('group_ids').split(',')
        keywords = self.get_argument('keywords')
        reply = self.get_argument('reply')

        mongo_obj = users.UserInfo().db
        mongo_obj[settings.auto_response_table].create_index('md5', unique=True)

        for group_id in group_ids:
            md5 = make_md5(reply + group_id)
            mongo_obj[settings.auto_response_table].insert({
                'md5': md5,
                'reply': reply,
                'group_id': group_id,
                'user_name': user_name
            })

        for keyword in keywords.split(','):
            for group_id in group_ids:
                md5 = make_md5(reply + group_id)
                mongo_obj[settings.groups_table].update({'group_id': group_id},
                                                        {'$addToSet': {'keywords': keyword}}, multi=True)
                mongo_obj[settings.auto_response_table].update(
                    {'md5': md5}, {'$addToSet': {'keywords': keyword}, '$set': {'switch': 'on'}}, multi=True)
        print(keywords)
        print(group_ids)
        print(reply)
        self.write({'msg': 'success'})


class Protect(tornado.web.RequestHandler):
    """
    违规监测
    """

    def get(self, user_name, *args, **kwargs):
        self.render('protect.html', user_name=user_name)

    def post(self, user_name, *args, **kwargs):
        groups = self.get_argument('groups')
        words = self.get_argument('words')
        switch = self.get_argument('switch')
        words_type = self.get_argument('words_type')
        table = users.UserInfo().db[settings.groups_table]
        table.update({'group_id': {'$in': groups}},
                     {'$set': {
                         settings.words_dict[words_type][0]: words,
                         settings.words_dict[words_type][1]: switch,
                     }}, multi=True)

        print(groups, words, switch, words_type)


class Jobs(tornado.web.RequestHandler):
    def post(self, user_name, *args, **kwargs):
        """
        定时群发处理, 获取用户对应的机器人名称，存储到mongo 同时 redis 发布任务
        """
        dct = {}
        dct['groups_id'] = self.get_argument('groups_id')  # 群id列表
        dct['content'] = self.get_argument('content')  # 发送内容
        # material_id = self.get_argument('material_id')      # 素材ID 列表
        dct['send_month'] = self.get_argument('send_month')  # 发送时间
        dct['send_day'] = self.get_argument('send_day')
        dct['send_hour'] = self.get_argument('send_hour')
        dct['send_minute'] = self.get_argument('send_minute')
        dct['job_id'] = make_md5(''.join([str(value) for key, value in dct.items()]))

        # 任务状态 0--未发送，1--发送成功，2--发送失败。 默认为0， 未发送
        dct['status'] = 0

        db = users.UserInfo().db

        # 查询用户对应robot
        user_table = db[settings.user_info_table]
        robot_name = user_table.find({'user_name': user_name}, {'robot_name': 1})

        # 查询素材id对应素材内容

        # 增加任务状态
        jobs_table = db[settings.jobs_table.format(user_name)]
        jobs_table.insert(dct)

        # redis发布任务
        conn_redis = redis.Redis(host=settings.redis_host, password=settings.redis_pwd)
        job_info = json.dumps(dct)
        conn_redis.publish(robot_name, job_info)

        print(dct)


dct = {}
dct['send_month'] = 6
dct['send_day'] = 18
dct['send_hour'] = 13
dct['send_minute'] = 49
dct['content'] = 'test'
conn_redis = redis.Redis(host=settings.redis_host, password=settings.redis_pwd)
job_info = json.dumps(dct)
conn_redis.publish('robot1', job_info)
