import requests
import pymysql
from bs4 import BeautifulSoup
from plugins import proxy
from faker import Factory


# def get_ua(url):
#     proxies = proxy.get_proxies()
#     headers = {
#         'User-Agent': Factory().create().user_agent(),
#         'Referer': 'https://www.baidu.com'
#     }
#     res = requests.get(url, headers=headers, proxies=proxy.get_proxy(proxies)[-1], verify=False)
#     html = res.text
#     soup = BeautifulSoup(html, 'lxml')
#     for item in soup.select('table.table.table-bordered > tr')[1::]:
#         phone_type = item.select('td')[0].text
#         phone_system = item.select('td')[1].text
#         browser_type = item.select('td')[2].text
#         user_agent = item.select('td')[3].text


def download_ua():
    proxies = proxy.get_proxies()
    headers = {
        'User-Agent': Factory().create().user_agent(),
        'Referer': 'https://www.baidu.com'
    }
    url_lst = ['http://www.fynas.com/ua/search?d=&b=&k=&page={}'.format(x) for x in range(1, 50)]
    mysql = {
        'user': 'root',
        'password': '123456',
        'host': '127.0.0.1',
        'port': 3306,
        'db': 'spider',
        'charset': 'utf8'
    }
    conn = pymysql.connect(**mysql)
    cursor = conn.cursor()
    execute = cursor.execute
    for url in url_lst:
        res = requests.get(url, headers=headers, proxies=proxy.get_proxy(proxies)[-1], verify=False)
        html = res.text
        soup = BeautifulSoup(html, 'lxml')
        for item in soup.select('table.table.table-bordered > tr')[1::]:
            phone_type = item.select('td')[0].text
            phone_system = item.select('td')[1].text
            browser_type = item.select('td')[2].text
            user_agent = item.select('td')[3].text
            execute('select user_agent from ua')
            result = cursor.fetchall()
            if (user_agent,) not in result:
                execute(
                    'insert into ua(phone_type, phone_system, browser_type, user_agent) values ("{}","{}","{}","{}")'.format(
                        phone_type, phone_system, browser_type, user_agent))
                conn.commit()
        headers['Referer'] = url
    cursor.close()
    conn.close()


def get_ua(ua_type):
    mysql = {
        'user': 'root',
        'password': '123456',
        'host': '127.0.0.1',
        'port': 3306,
        'db': 'spider',
        'charset': 'utf8'
    }
    conn = pymysql.connect(**mysql)
    cursor = conn.cursor()
    execute = cursor.execute
    sql = """select user_agent from ua where browser_type like '%{}%'""".format(ua_type)
    execute(sql)
    result = [x[0] for x in cursor.fetchall()]
    cursor.close()
    conn.close()
    return result


if __name__ == '__main__':
    # download_ua()
    for ua in get_ua('浏览器'):
        print(ua)
