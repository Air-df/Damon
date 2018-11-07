import re
import time
import random
import traceback
import requests

from bs4 import BeautifulSoup
from faker import Factory
from plugins import proxy

proxies = proxy.get_proxies()
# 页数
page_num = 2
# 搜索关键字
search_keyword = input('输入搜索关键字')
# 基础链接
base_url = 'https://www.baidu.com'

url = 'https://www.baidu.com/s?rtt=1&bsst=1&cl=2&tn=news&word={}'.format(search_keyword)
headers = {
    'User-Agent': Factory().create().user_agent(),
    'Referer': 'https://www.baidu.com'
}


def get_data(url):
    global page_num
    res = requests.get(url, headers=headers, proxies=proxy.get_proxy(proxies)[-1], verify=False)
    html = res.text
    soup = BeautifulSoup(html, 'lxml')
    for item in soup.select('div.result'):
        dct = {}
        # 标题
        try:
            dct['title'] = re.sub('\n *| *\n', '', item.select('h3 > a')[0].text)
            # 链接
            link = item.select('h3 > a')[0].get('href')
            dct['link'] = link
        except:
            continue
        try:
            # 发布时间
            date = item.select('p.c-author')[0].text.split()[1::]
            dct['date'] = ' '.join(date)
            # 发布媒体
            dct['resource_from'] = item.select('p.c-author')[0].text.split()[0]
            # 概要
            brief = ''.join(item.select('div.c-summary.c-row ')[0].text.split()[1:-1:])
            dct['brief'] = re.sub(''.join(date), '', brief)
        except:
            dct['resource_from'], dct['date'] = '', ''
        print(dct)
    # 下一页链接
    try:
        next_page = soup.select('p#page a')[-1].get('href')
        next_page_url = base_url + next_page
        print('开始第{}页'.format(page_num), next_page_url, sep='\n')
        time.sleep(random.uniform(3, 7))
        page_num += 1
        get_data(next_page_url)
    except Exception as e:
        traceback.print_exc()
        print('end')
        get_data(url)


get_data(url)
