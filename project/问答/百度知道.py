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
    'Referer': 'https://www.baidu.com'
}
proxies = proxy.get_proxies()
search_keyword = input('输入关键字')
start_url = 'https://zhidao.baidu.com/search?lm=0&rn=10&pn=0&fr=search&ie=gbk&word={}'.format(search_keyword)


def get_qw():
    res = requests.get(start_url, headers=headers, proxies=proxy.get_proxy(proxies)[-1], verify=False)
    qw = res.url.split('&')[-1]
    return qw


def get_data(url):
    res = requests.get(url, headers=headers, proxies=proxy.get_proxy(proxies)[-1], verify=False)
    res.encoding = 'gbk'
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


def go():
    qw = get_qw()
    base_url = 'https://zhidao.baidu.com/search?{}&ie=gbk&site=-1&sites=0&date=0&pn={}'
    url_lst = [base_url.format(qw, (x-1) * 10) for x in range(1, 77)]
    for url in url_lst:
        get_data(url)


go()