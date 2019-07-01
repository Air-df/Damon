import time
import settings

from tornado.web import RequestHandler
from modules import users


def get_time(timestamp=int(time.time())):
    """
    unix时间转换 -- 微信使用
    :param num:
    :return: 日期
    """
    format = '%Y.%m.%d %H:%M:%S'
    value = time.localtime(timestamp)
    dt = time.strftime(format, value)
    return dt


class Count(RequestHandler):
    def post(self, *args, **kwargs):
        func_dict = {
            '1': self.activity,
            '2': self.word_frequency
        }
        data_type = self.get_argument('data_type')
        if data_type in func_dict:

            func_dict[data_type]()
        else:
            self.error('未知请求')

    def get_time(self, timestamp=int(time.time())):
        """
        unix时间转换 -- 微信使用
        :param num:
        :return: 日期
        """
        format = '%Y.%m.%d %H:%M:%S'
        value = time.localtime(timestamp)
        dt = time.strftime(format, value)
        return dt

    def activity(self):
        db = users.UserInfo().db
        user_name = self.get_argument('user_name')

        # 数据时间段
        start_time = self.get_argument('start_time')
        end_time = self.get_argument('end_time')

        group_table = db[settings.groups_table]
        member_table = db[settings.member_ids_table.format(user_name)]
        dialogue_table = db[settings.dialogue_history_table.format(user_name)]
        print('activity')
        # 总群数
        groups_count = group_table.find({'user_name': user_name}, {}).count()
        # 总用户数
        member_count = len(member_table.distinct('member_id'))
        # 当日入群人数， 历史退群人数
        member_join_count = member_table.find({'join_time': {'$regex': '{}.+'.format(get_time().split()[0])}}).count()
        member_quit_count = member_table.find({'quit_time': {'$exists': True}}).count()
        # 群消息数
        msg_count = dialogue_table.find().count()
        # 发言人数

        # 消息数据  每天，对应总消息数，默认为一周

        # 消息类型占比    文本、图片、链接、小程序、其他 各种消息类型占比

        # 用户占比  每天对应的，群总人数、活跃人数

        # 分时消息分布   最近一周内，每个小时内的总消息量

        self.success()

    def word_frequency(self):
        print('frequency')
        self.success()

    def success(self):
        self.write({'status': 1})

    def error(self, info):
        self.write({'status': 0, 'info': info})


if __name__ == '__main__':
    db = users.UserInfo().db
    user_name = 'test2'
    group_table = db[settings.groups_table]
    member_table = db[settings.member_ids_table.format(user_name)]
    dialogue_table = db[settings.dialogue_history_table.format(user_name)]

    member_join_count = member_table.find({'join_time': {'$regex': '{}.+'.format(get_time().split()[0])}}).count()
    member_quit_count = member_table.find({'quit_time': {'$exists': True}}).count()
    print(member_join_count, member_quit_count)

    print(get_time(int(time.time() - 24 * 2 * 3600)).split()[0])
