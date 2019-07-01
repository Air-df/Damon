import pymongo
import settings


class ModuleBase:
    def __init__(self):
        self.conn_mongo = pymongo.MongoClient(host=settings.mongo_host)
        self.db = self.conn_mongo[settings.mongo_db]


class UserInfo(ModuleBase):
    def __init__(self):
        super().__init__()
        self.table = self.db[settings.user_info_table]
        self.table.ensure_index('user_name', unique=True)
        self.table.ensure_index('phone', unique=True)

    def check_is_exist(self, **kwargs):
        is_exist = [item for item in self.table.find(kwargs, {})]
        # print(True if is_exist == [] else False)
        return True if is_exist == [] else False

    def insert(self, **kwargs):
        self.table.insert(kwargs)


if __name__ == '__main__':
    # user_info = UserInfo()
    # user_info.check_is_exist(**{'user_name': 'user name test'})
    # user_info.check_is_exist(**{'user_name': '1', 'pwd': '3'})

    db = UserInfo()
    # is_first = db.table.find({'user_name': 'test'}, {'is_first': 1, '_id': 0})
    # print(type(is_first[0]['is_first']))
    # user_name = db.table.find({'robot_name': 'robot1'}, {'_id': 0, 'user_name': 1})[0]['user_name']
    groups = list(db.db[settings.groups_table].find({'user_name': 'test2', 'keywords': {'$exists': True}},
            {'_id': 0, 'keywords': 1}))
    for group in groups:
        print(group)
    print(groups)

    # db.table.update({'user_name': 'test'}, {'$set': {'robot_name': 'robot_name', 'is_first': 0, 'wechat_id': 'wechat_id'}})
    # user_info.insert(**{'user_name': 'user name test', 'phone': 123456})