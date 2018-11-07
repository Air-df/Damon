import re
import time
import random
import traceback
import requests

from bs4 import BeautifulSoup
from faker import Factory
from plugins import proxy

"""
各板块采用ajax请求
可以找到对应的api接口
"""

headers = {
    'User-Agent': Factory().create().user_agent(),
    'Referer': 'https://www.baidu.com'
}
proxies = proxy.get_proxies()
# 首页
url_home = 'http://sh.qihoo.com/'
url_example = 'http://sh.qihoo.com/world/'
news_type = {
    '国内': 'china',
    '国际': 'world',
    '社会': 'society',
    '党媒': 'dangmei',
    '军事': 'mil',
    '娱乐': 'ent',
    '财经': 'business',
    '体育': 'sports',
    '教育': 'edu',
    '房产': 'house',
    '女人': 'woman',
    '汽车': 'auto',
    '科技': 'sci',
    '互联网': 'internet',
    '游戏': 'game',
    '公益': 'gongyi',
    '图片': 'image',
}


def parse_home(url):
    res = requests.get(url, headers=headers, proxies=proxy.get_proxy(proxies)[-1], verify=False)
    html = res.text
    soup = BeautifulSoup(html, 'lxml')
    for a in soup.select('div.box-news a'):
        dct = {}
        try:
            dct['title'] = ''.join(a.text.split())
            dct['link'] = a.get('href')
            if 'http' in dct['link']:
                print(dct)
        except:
            traceback.print_exc()
            print(a)


parse_home(url_home)