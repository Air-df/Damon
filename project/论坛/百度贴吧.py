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

headers = {
    'User-Agent': Factory().create().user_agent(),
    'Referer': 'https://tieba.baidu.com/index.html'
}
proxies = proxy.get_proxies()
search_keyword = input('输入关键字')
start_url = 'http://tieba.baidu.com/f/search/res?ie=utf-8&qw={}'.format(search_keyword)


def get_qw():
    res = requests.get(start_url, headers=headers, proxies=proxy.get_proxy(proxies)[-1], verify=False)
    qw = res.url.split('&')[-1]
    return qw


# 全吧搜索--共76页
def get_data(url):
    res = requests.get(url, headers=headers, proxies=proxy.get_proxy(proxies)[-1], verify=False)
    html = res.text
    soup = BeautifulSoup(html, 'lxml')
    base_url = 'https://tieba.baidu.com'
    for item in soup.select('div.s_post'):
        dct = {}
        try:
            dct['title'] = ''.join(item.select('span.p_title a')[0].text.split())
            dct['brief'] = ''.join(item.select('div.p_content')[0].text.split())
            # 信息来源--贴吧名称
            dct['resource_from'] = item.select('font.p_violet')[0].text
            # 贴吧作者
            dct['username'] = item.select('font.p_violet')[1].text
            dct['date'] = item.select('font.p_green.p_date')[0].text
            dct['link'] = base_url + item.select('span.p_title a')[0].get('href')
            print(dct)
        except:
            pass

    headers['Referer'] = url
    return True


def go():
    qw = get_qw()
    base_url = 'http://tieba.baidu.com/f/search/res?isnew=1&kw=&{}&rn=10&un=&only_thread=0&sm=1&sd=&ed=&pn={}'
    url_lst = [base_url.format(qw, x) for x in range(1, 77)]
    for url in url_lst:
        time.sleep(random.uniform(3, 5))
        get_data(url)


go()