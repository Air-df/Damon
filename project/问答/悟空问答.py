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
js加载，返回json格式
地址 offset控制页数
https://www.wukong.com/wenda/web/search/loadmore/?search_text=%E7%AF%AE%E7%90%83&offset=10&count=10
"""

headers = {
    'User-Agent': Factory().create().user_agent(),
    'Referer': 'https://www.wukong.com/'
}
proxies = proxy.get_proxies()
search_keyword = input('输入关键字')
start_url = 'https://www.wukong.com/search/?keyword={}'.format(search_keyword)


def get_qw():
    res = requests.get(start_url, headers=headers, proxies=proxy.get_proxy(proxies)[-1], verify=False)
    qw = res.url.split('?')[-1]
    return qw


def get_data(url):
    res = requests.get(url, headers=headers, proxies=proxy.get_proxy(proxies)[-1], verify=False)
    data = json.loads(res.text)
    # print(data)
    base_url = 'https://www.wukong.com/question/'
    for item in data['data']['feed_question']:
        dct = {}
        dct['title'] = item['question']['title']
        # 链接
        dct['link'] = base_url + item['question']['qid']
        try:
            # 回答内容
            dct['brief'] = item['ans_list'][0]['content_abstract']
            # 回答者
            dct['username'] = item['ans_list'][0]['user']['uname']
            # 回答时间
            dct['date'] = item['ans_list'][0]['show_time']
            # 点赞数量
            dct['like'] = item['ans_list'][0]['digg_count']
        except:
            traceback.print_exc()
            pass
        print(dct)
    headers['Referer'] = url
    return True


def go():
    qw = get_qw()
    base_url = 'https://www.wukong.com/wenda/web/search/loadmore/?search_text={}&offset={}&count=10'
    url_lst = [base_url.format(qw, (x-1) * 10) for x in range(1, 10)]
    for url in url_lst:
        get_data(url)
        time.sleep(random.uniform(3, 5))


# get_data('https://www.wukong.com/wenda/web/search/loadmore/?search_text=%E7%AF%AE%E7%90%83&offset=0&count=10')
go()