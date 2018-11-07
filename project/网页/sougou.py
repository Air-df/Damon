import re
import time
import random
import traceback

from bs4 import BeautifulSoup
from selenium import webdriver
from plugins import proxy

# page--页数
page_num = 2
# query--搜索关键字
search_keyword = input('输入关键字')
# 有效时间
search_time = ['一天', '一周', '一月', '一年']
# 基础链接--生成链接使用
base_url = 'https://www.sogou.com'


def make_service_args():
    global proxies
    types = proxy.get_proxy(proxies)[2]
    ip = proxy.get_proxy(proxies)[0]
    port = proxy.get_proxy(proxies)[1]
    prox = '{}://{}:{}'.format(types, ip, port)
    service_args = [
        '--proxy={}'.format(prox),  # 代理http://IP:PORT 只设置该项也可以
        '--proxy-type={}'.format(types),  # 代理类型：http/https
        '--load-images=no',  # 图片加载开关
        '--disk-cache=yes',  # 缓存控制
        '--ignore-ssl-errors=true',  # 忽略ssl错误
    ]
    return service_args


driver = webdriver.PhantomJS()
driver.get('https://www.sogou.com')


def get_html():
    global page_num
    driver.find_element_by_id('query').send_keys(search_keyword)
    driver.find_element_by_id('stb').click()
    time.sleep(1)
    while 1:
        html = driver.page_source
        url = driver.current_url
        print(url)
        parse(html)
        if 'page' in url:
            next_page = re.sub('&page=\d+', '&page={}'.format(page_num), url)
            driver.get(next_page)
            page_num += 1
            time.sleep(random.uniform(2, 5))
        else:
            driver.get(url + '&page={}'.format(page_num))


def parse(html):
    # print(html)
    soup = BeautifulSoup(html, 'lxml')
    for item in soup.select('div.results > div'):
        dct = {}
        # 标题
        try:
            dct['title'] = item.select('h3 a')[0].text
            # 链接
            link = item.select('h3 a')[0].get('href')
            if 'http' not in link:
                link = base_url + link
            dct['link'] = link
            # 概要
            dct['brief'] = re.sub(r'\n|\xa0|  |\t', '', item.select('div')[0].text)
            # 发布媒体
            dct['resource_from'] = item.select('cite')[0].text.split()[0]
        except:
            continue
        # 发布时间
        try:
            regex = re.compile(r'\d{4}-\d{1,2}-\d{1,2}|\d*[小-时-天-月]{1,2}前')
            dct['date'] = regex.findall(item.select('div.fb > cite')[0].text)[0]
        except:
            dct['date'] = 'null'
        print(dct)


if __name__ == '__main__':
    # get_data(url)
    get_html()
    driver.close()
