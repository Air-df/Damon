import settings
import tornado.web
from modules import users


class RegisterHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.render('register.html', server_host=settings.server_host, server_port=settings.server_port)

    def post(self, *args, **kwargs):
        # 返回信息 error_type 1---- 输入密码不一致；2----用户名已存在；3----手机号已存在
        msg = {'is_success': 0, 'error_type': 1, 'info': ''}
        dct = {}
        dct['user_name'] = self.get_argument('user_name')
        dct['pwd'] = self.get_argument('pwd')
        dct['repwd'] = self.get_argument('repwd')
        dct['phone'] = self.get_argument('phone')
        dct['is_first'] = 1

        if dct['pwd'] != dct['repwd']:
            msg['info'] = '两次密码不一致'
            self.write(msg)
            return
        user_info = users.UserInfo()
        result_user_name = user_info.check_is_exist(**{'user_name': dct['user_name']})
        if not result_user_name:
            msg['error_type'] = 1
            msg['info'] = '用户名已存在'
            self.write(msg)
            return
        result_phone = user_info.check_is_exist(**{'phone': dct['phone']})
        if not result_phone:
            msg['error_type'] = 2
            msg['info'] = '该手机号已注册'
            self.write(msg)
            return
        msg['is_success'] = 1
        msg['error_type'] = 0
        user_info.insert(**dct)
        msg['info'] = '注册成功'
        self.write(msg)
