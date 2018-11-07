import random
import pymysql

"""
本模块用于生成代理
"""


def get_proxies():
    mysql = {
        'user': 'root',
        'password': 'kongqi8023',
        'host': '127.0.0.1',
        'port': 3306,
        'db': 'spider',
        'charset': 'utf8'
    }
    conn = pymysql.connect(**mysql)
    cursor = conn.cursor()
    execute = cursor.execute
    sql = 'select ip, port, types from proxies limit 500'
    execute(sql)
    proxies = cursor.fetchall()
    cursor.close()
    conn.close()
    return proxies


# 随机选择IP
def get_proxy(proxies):
    proxy = random.choice(proxies)
    ip = proxy[0]
    port = proxy[1]
    types = proxy[2]
    proxy = '{}://{}:{}'.format(ip, port, types)
    proxy = {types: proxy}
    return (ip, port, types, proxy)


if __name__ == '__main__':
    proxies = get_proxies()
    result = get_proxy(proxies)
    print(result)