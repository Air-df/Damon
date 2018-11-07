import re
import time
import random
import traceback
import requests

from bs4 import BeautifulSoup
from faker import Factory
from plugins import proxy

"""
待调试，不稳定，获取第一页后之后没有数据
"""
proxies = proxy.get_proxies()
# 搜索关键字
search_keyword = input('输入关键字：')

start_url = 'https://so.tv.sohu.com/mts?box=1&wd={}'.format(search_keyword)
headers = {
    'User-Agent': Factory().create().user_agent(),
    'Referer': 'https://tv.sohu.com/'
}


def get_qw():
    res = requests.get(start_url, headers=headers, proxies=proxy.get_proxy(proxies)[-1], verify=False)
    qw = res.url.split('&')[-1]
    return qw


def get_data(url):
    res = requests.get(url, headers=headers, proxies=proxy.get_proxy(proxies)[-1], verify=False)
    html = res.text
    print(html)
    soup = BeautifulSoup(html, 'lxml')
    base_url = ''
    for item in soup.select('ul.list170.cfix > li'):
        dct = {}
        try:
            dct['title'] = ''.join(item.select('strong.lt-title')[0].text.split())
            # 播放量
            dct['acount'] = ''.join(item.select('span.acount')[0].text.split())
            # 时长
            dct['radio_time'] = ''.join(item.select('span.maskTx')[0].text.split())
            a_lst= item.select('p.lt-info a')
            # 发布时间
            dct['pub_time'] = a_lst[-1].text
            if len(a_lst) == 1:
                dct['resource_from'] = ''
            else:
                dct['resource_from'] = a_lst[0].text
            print(dct)
            dct['link'] = item.select('strong.lt-title a')[0].get('href')
        except:
            traceback.print_exc()
            pass
    headers['Referer'] = url
    return True


def go():
    qw = get_qw()
    base_url = 'https://so.tv.sohu.com/mts?wd={}&c=0&v=0&length=0&limit=0&site=0&o=0&p={}&st=0&suged=&filter=0'
    url_lst = [base_url.format(qw, x) for x in range(1, 77)]
    for url in url_lst:
        get_data(url)
        time.sleep(random.uniform(3, 5))


go()