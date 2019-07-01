import json
import tornado.web
import random
import redis
import settings

from modules import users


class RedirectHandler(tornado.web.RequestHandler):
    def get(self, user_name, *args, **kwargs):
        user_name = user_name
        base_path = '../static/qrcs/'

        table = users.UserInfo().table
        try:
            is_first = table.find({'user_name': user_name}, {'is_first': 1, '_id': 0})[0]['is_first']
        except:
            return

        if not is_first:
            self.redirect('/u/{}/control'.format(user_name))
        else:
            # 将没有绑定的小助手，随机选择一个二维码, 文件名，
            robot_name = 'robot1'
            qrc_path = base_path + 'qrc1.png'

            # 生成验证码
            captcha_num = ''.join([str(random.randint(1, 9)) for x in range(4)])
            self.render('init.html', qrc_path=qrc_path, captcha_num=captcha_num, websocket_host=settings.websocket_host,
                        control_url=settings.control_url)
            print(user_name, qrc_path, captcha_num)
            # 将验证码及用户名存入redis
            self.captcha_to_redis(robot_name, user_name, captcha_num)

    def post(self, *args, **kwargs):
        self.redirect('https://www.baidu.com')

    def captcha_to_redis(self, robot_name, user_name, captcha_num):
        conn_redis = redis.Redis(host=settings.redis_host, password=settings.redis_pwd, db=13)
        conn_redis.set(robot_name, json.dumps({'user_name': user_name, 'captcha_num': captcha_num}))
