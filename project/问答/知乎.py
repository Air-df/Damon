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
搜索后第一页会js代码里会有search_hash_id值，组合成json请求网址
json 请求网址
offset 代表页数 search_hash_id代表搜索内容
https://www.zhihu.com/api/v4/search_v3?t=general&q=%E7%94%B5%E5%BD%B1%E6%8E%A8%E8%8D%90&correction=1&offset=15&limit=10&show_all_topics=0&search_hash_id=b01966ccbd0858b86f7e0612df3fba31
"""
proxies = proxy.get_proxies()
# 页数
page_num = 2
# 搜索关键字
search_keyword = input('输入搜索关键字')
# 基础链接
base_url = ''

start_url = 'https://www.zhihu.com/search?type=content&q={}'.format(search_keyword)
headers = {
    'User-Agent': Factory().create().user_agent(),
    'Referer': 'https://www.zhihu.com/search?type=content&q=%E8%96%9B%E4%B9%8B%E8%B0%A6',
    'Connection': 'keep-alive',
}


def get_para():
    driver = webdriver.PhantomJS()
    driver.get('https://www.zhihu.com/explore')
    driver.find_element_by_id('q').send_keys(search_keyword)
    driver.find_element_by_class_name('zu-top-search-button').click()
    time.sleep(2)
    url = driver.current_url
    html = driver.page_source
    q = url.split('&')[-1]
    print(driver.get_cookies())
    regex = re.compile(r'search_hash_id=(.*)')
    search_id = regex.findall(html)
    return q, search_id


def get_data(url):
    res = requests.get(url, headers=headers, proxies=proxy.get_proxy(proxies)[-1], verify=False)
    html = res.text
    dct = json.loads(html)


print(get_para())