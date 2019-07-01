import tornado.web
import tornado.ioloop
import tornado.httpserver
import json
import os
import time
import datetime
import threading
import re
import tornado.websocket

from multiprocessing import Process
from views import login, register, control, init, auto_response, welcome, protect, data_count


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    users = set()
    users_dct = {}

    def open(self):
        print(self)
        print('open')

    def on_close(self):
        for name, client in self.users_dct.items():
            if client == self:
                self.users_dct.pop(name)
                break
        print(self.users_dct)
        print('close')

    def on_message(self, msg):
        print(msg)
        self.write_message(json.dumps({'from_user': 'test2', 'msg': 'msg', 'msg_type': 1}))

        info_dct = json.loads(msg)
        msg_type = info_dct['msg_type']
        func_dct = {1: self.deal_msg_type_1, 2: self.deal_msg_type_2, 3: self.deal_msg_type_3, 4: self.deal_msg_type_4}
        func_dct[msg_type](**info_dct)

    def callback(self, count):
        self.write_message(count)

    def deal_msg_type_1(self, **kwargs):
        """
        初次连接处理
        :param kwargs:
        :return:
        """
        self.users_dct[kwargs['from_user']] = self
        print(kwargs)
        print(self.users_dct)

    def deal_msg_type_2(self, **kwargs):
        """
        聊天信息处理
        根据用户名，找到对应robot，及微信群id，向对应的群内发送消息
        :param user_name:
        :return:
        """
        # 判断是否在线
        if kwargs['to_user'] in self.users_dct:
            self.users_dct[kwargs['to_user']].write_message(json.dumps(kwargs))

        print(2)
        print(kwargs)

    def deal_msg_type_3(self, **kwargs):
        """
        处理，用户初始化，更新用户状态信息
        :param msg:
        :return:
        """
        print(3)
        print(kwargs)

    def deal_msg_type_4(self, **kwargs):
        self.users_dct[kwargs['to_user']].write_message(json.dumps(kwargs))


if __name__ == '__main__':
    import settings

    setting = {
        'template_path': 'templates',
        'static_path': 'static',
    }
    app = tornado.web.Application([
        ('/login', login.LoginHandler),
        ('/register', register.RegisterHandler),
        ('/history', control.HistoryHandler),
        ('/u/(?P<user_name>\w+)/control', control.ControlHandler),
        ('/u/(?P<user_name>\w+)/manage_group', control.GroupManager),
        ('/u/(?P<user_name>\w+)/welcome', control.Welcome),
        ('/u/(?P<user_name>\w+)/auto_response', control.AutoResponse),
        ('/u/(?P<user_name>\w+)/protect', control.Protect),
        ('/u/(?P<user_name>\w+)/jobs', control.Jobs),
        (r'/u/(?P<user_name>\w+)', init.RedirectHandler),
        (r'/autoresponse', auto_response.Handler),
        (r'/welcome', welcome.Handler),
        (r'/socket', WebSocketHandler),
        (r'/protect', protect.Config),
        (r'/count', data_count.Count),
    ], **setting)

    server = tornado.httpserver.HTTPServer(app)
    server.listen(settings.server_port)
    tornado.ioloop.IOLoop.instance().start()
