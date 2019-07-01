import settings

from tornado.web import RequestHandler
from modules import users


class Handler(RequestHandler):
    def post(self, *args, **kwargs):
        do = self.get_argument('set_type')
        response_info_id = self.get_argument('response_info_id')
        table = users.UserInfo().db[settings.auto_response_table]
        func_dct = {
            'stop': self.stop,
            'delete': self.delete,
            'start': self.start,
            'update': self.update
        }
        if do in func_dct:
            func_dct[do](table, response_info_id)
        else:
            self.write({'status': 0, 'info': '未知操作'})

    def stop(self, table, response_info_id):
        table.update({'md5': response_info_id}, {'$set': {'switch': 'off'}})
        self.write({'status': 1})

    def delete(self, table, response_info_id):
        table.update({'md5': response_info_id}, {'$set': {'is_delete': 1}})
        self.write({'status': 1})

    def start(self, table, response_info_id):
        table.update({'md5': response_info_id}, {'$set': {'switch': 'on'}})
        self.write({'status': 1})

    def update(self):
        keywords = self.get_argument('keywords')
        reply = self.get_argument('reply')
        group_ids = self.get_argument('group_ids')