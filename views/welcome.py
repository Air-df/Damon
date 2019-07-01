import settings

from tornado.web import RequestHandler
from modules import users


class Handler(RequestHandler):
    def post(self, *args, **kwargs):
        set_type = self.get_argument('set_type')
        group_id = self.get_argument('group_id')
        table = users.UserInfo().db[settings.groups_table]
        func_dct = {
            'stop': self.stop,
            'delete': self.delete,
            'start': self.start
        }
        if set_type in func_dct:
            func_dct[set_type](table, group_id)
        else:
            self.write({'status': 0, 'info': '未知操作'})

    def stop(self, table, group_id):
        table.update({'group_id': group_id}, {'$set': {'switch': 'off'}})
        self.write({'status': 1})

    def delete(self, table, group_id):
        table.update({'group_id': group_id}, {'$set': {'is_delete': 1}})
        self.write({'status': 1})

    def start(self, table, group_id):
        table.update({'md5': group_id}, {'$set': {'switch': 'on'}})
        self.write({'status': 1})
