import tornado.web
import settings
from modules import users


class LoginHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        print(self.request.headers._dict)
        self.render('login.html', server_host=settings.server_host, server_port=settings.server_port)

    def post(self, *args, **kwargs):
        dct = {}
        msg = {'is_success': 0, 'info': '账户名或密码错误'}
        dct['user_name'] = self.get_argument('user_name')
        dct['pwd'] = self.get_argument('pwd')
        user_info = users.UserInfo()
        is_exist = user_info.check_is_exist(**dct)
        if not is_exist:
            msg['is_success'] = 1
            self.write(msg)
        else:
            self.write(msg)
