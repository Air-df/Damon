import re
import time
import json
import random
import traceback
import requests

from selenium import webdriver
from bs4 import BeautifulSoup
from faker import Factory
from plugins import proxy, time_now

"""
pc端有限制，考虑wap端，wap端为js加载，返回格式为html
https://m.wenda.so.com/search/get?pn=页码&q=关键字&tpl=ajax%2Fsearch%2Fajax_search_list&t=时间
"""
headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; U; Android 4.1.1; zh-cn;  MI2 Build/JRO03L) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30 XiaoMi/MiuiBrowser/1.0',
    'Referer': 'https://m.wenda.so.com/'
}
proxies = proxy.get_proxies()
search_keyword = input('输入关键字')
start_url = 'https://m.wenda.so.com/search/?q={}'.format(search_keyword)


def get_qw():
    res = requests.get(start_url, headers=headers, proxies=proxy.get_proxy(proxies)[-1], verify=False)
    qw = res.url.split('?')[-1]
    return qw


# def get_pc_data(url):
#     res = requests.get(url, headers=headers, proxies=proxy.get_proxy(proxies)[-1], verify=False)
#     html = res.text
#     print(html)
#     soup = BeautifulSoup(html, 'lxml')
#     base_url = 'https://wenda.so.com'
#     for item in soup.select('li.item.js-normal-item'):
#         dct = {}
#         try:
#             dct['title'] = ''.join(item.select('div.qa-i-hd')[0].text.split())
#             # 回答内容
#             dct['brief'] = ''.join(item.select('div.qa-i-bd')[0].text.split())
#             detail = item.select('div.qa-i-ft')[0].text.split('-')
#             # 分类
#             dct['resource_from'] = ''.join(detail[0].split())
#             # 提问时间
#             dct['date'] = ''.join(detail[-1].split())
#             # 回答数量
#             dct['answer_count'] = ''.join(detail[1].split())
#             dct['link'] = base_url + item.select('div.qa-i-hd a')[0].get('href')
#             print(dct)
#         except:
#             traceback.print_exc()
#             pass
#     headers['Referer'] = url
#     return True

# def go_pc():
#     qw = get_qw()
#     base_url = 'http://wenda.so.com/search/?{}&pn={}'
#     url_lst = [base_url.format(qw, (x-1) * 10) for x in range(1, 101)]
#     for url in url_lst:
#         get_wap_data(url)
#         # get_pc_data(url)
#         time.sleep(random.uniform(5, 8))


def get_wap_data(url):
    res = requests.get(url, headers=headers, proxies=proxy.get_proxy(proxies)[-1], verify=False)
    html = json.loads(res.text)['result']
    soup = BeautifulSoup(html, 'lxml')
    base_url = 'https://m.wenda.so.com'
    for item in soup.select('li.search-list-item.g-wrap'):
        dct = {}
        try:
            dct['title'] = ''.join(item.select('a')[0].text.split())
            # 回答内容
            dct['brief'] = ''.join(item.select('a')[1].text.split())
            detail = item.select('div')[0]
            # 提问时间
            dct['date'] = ''.join(detail.select('span')[1].text.split())
            # 回答数量
            dct['answer_count'] = re.findall('\d+', detail.select('a')[0].text)[0]
            dct['link'] = base_url + item.select('a')[0].get('href')
            print(dct)
        except:
            traceback.print_exc()
            pass
    headers['Referer'] = url
    return True


def go_wap():
    qw = get_qw()
    base_url = 'https://m.wenda.so.com/search/get?pn={}&{}&tpl=ajax%2Fsearch%2Fajax_search_list&t=1540964660158'
    url_lst = (base_url.format(x, qw, time_now.now()) for x in range(1, 101))
    for url in url_lst:
        get_wap_data(url)
        # get_pc_data(url)
        time.sleep(random.uniform(5, 8))


go_wap()
