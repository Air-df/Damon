import re
import time
import json
import random
import traceback
import requests

from selenium import webdriver
from bs4 import BeautifulSoup
from faker import Factory
from plugins import proxy


"""
js 加载，返回json数据
"""

headers = {
    'User-Agent': Factory().create().user_agent(),
    'Referer': 'https://www.baidu.com'
}
proxies = proxy.get_proxies()


def get_data(url):
    res = requests.get(url, headers=headers, proxies=proxy.get_proxy(proxies)[-1], verify=False)
    html = res.text
    # print(html)
    soup = BeautifulSoup(html, 'lxml')
    base_url = ''
    for item in soup.select('div#wgt-list  dl'):
        dct = {}
        try:
            dct['title'] = ''.join(item.select('dt.dt.mb-4.line a')[0].text.split())
            # 回答内容
            dct['brief'] = ''.join(item.select('dd.dd.answer')[0].text.split())
            # 回答者
            dct['username'] = ''.join(item.select('dd.dd.explain.f-light span')[1].text.split())
            # 回答时间
            dct['date'] = item.select('dd.dd.explain.f-light span')[0].text
            # 回答数量
            dct['link'] = item.select('dd.dd.explain.f-light span')[1].text
            # 点赞数量
            dct['like'] = item.select('dd.dd.explain.f-light span')[-1].text
            print(dct)
        except:
            traceback.print_exc()
            pass
    headers['Referer'] = url
    return True

