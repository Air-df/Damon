import settings

from tornado.web import RequestHandler
from modules import users


class Config(RequestHandler):
    def post(self, *args, **kwargs):
        protect_type = self.get_argument('protect_type')
        switch = self.get_argument('switch')
        group_ids = self.get_argument('group_ids')
        words = self.get_argument('words')
