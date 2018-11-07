import time
import json
import random
import traceback
import requests

from bs4 import BeautifulSoup
from faker import Factory
from plugins import proxy

headers = {
    'User-Agent': Factory().create().user_agent(),
    'Referer': 'http://bbs.tianya.cn'
}
proxies = proxy.get_proxies()
search_keyword = input('输入关键字：')
start_url = 'http://search.tianya.cn/bbs?q={}'.format(search_keyword)


def get_qw():
    res = requests.get(start_url, headers=headers, proxies=proxy.get_proxy(proxies)[-1], verify=False)
    qw = res.url.split('?')[-1]
    return qw


def get_comments(url):
    res = requests.get(url, headers=headers, proxies=proxy.get_proxy(proxies)[-1], verify=False)
    html = res.text
    soup = BeautifulSoup(html, 'lxml')
    for item in soup.select('div.searchListOne > ul > li'):
        dct = {}
        try:
            dct['title'] = ''.join(item.select('h3 a')[0].text.split())
            dct['brief'] = ''.join(item.select('div p')[0].text.split())
            # 信息来源--贴吧名称
            dct['resource_from'] = item.select('p.source a')[0].text
            # 贴吧作者
            dct['username'] = item.select('p.source a')[1].text
            dct['date'] = item.select('p.source span')[0].text
            # 回复数量
            dct['reply'] = item.select('p.source span')[0].text
            dct['link'] = item.select('h3 a')[0].get('href')
            print(dct)
        except:
            pass


def go():
    qw = get_qw()
    base_url = 'http://search.tianya.cn/bbs?{}&pn={}'
    url_lst = [base_url.format(qw, x) for x in range(1, 77)]
    for url in url_lst:
        print(url)
        get_comments(url)
        time.sleep(random.uniform(3, 5))


go()


