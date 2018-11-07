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
主页搜索----》获取商品ID及链接，链接用作referer----》拿评论数据
评论数据为js加载，json格式，地址为
https://sclub.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98vv2748&productId=7390561&score=0&sortType=5&page=0&pageSize=10&isShadowSku=0&fold=1 HTTP/1.1
https://sclub.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98vv2748&productId=7390561&score=0&sortType=5&page=1&pageSize=10&isShadowSku=0&rid=0&fold=1 HTTP/1.1
https://sclub.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98vv2748&productId=7390561&score=0&sortType=5&page=2&pageSize=10&isShadowSku=0&rid=0&fold=1 HTTP/1.1
所需参数
callback=fetchJSON_comment98vv2748
productId=7390561
page=5
其他为常量
"""
headers = {
    'User-Agent': Factory().create().user_agent(),
    'Referer': 'https://www.jd.com/'
}
proxies = proxy.get_proxies()
search_keyword = input('输入关键字')
start_url = 'https://search.jd.com/Search?keyword={}&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq={}&page=1&s=1&click=0'.format(
    search_keyword, search_keyword)


def get_qw():
    res = requests.get(start_url, headers=headers, proxies=proxy.get_proxy(proxies)[-1], verify=False)
    qw = res.url.split('&')[-4]
    return qw


# 解析搜索结果
def get_product_id(url):
    res = requests.res = requests.get(url, headers=headers, proxies=proxy.get_proxy(proxies)[-1], verify=False)
    res.encoding = 'utf-8'
    html = res.text
    # print(html)
    soup = BeautifulSoup(html, 'lxml')
    base_url = 'https:'
    id_lst = []
    for item in soup.select('div.gl-i-wrap'):
        dct = {}
        # 商品名称
        dct['product_name'] = ''.join(item.select('div.p-name.p-name-type-2 em')[0].text.split())
        # 商品价格
        dct['price'] = item.select('div.p-price i')[0].text
        # 评论数量
        dct['comment_account'] = ''.join(item.select('div.p-commit a')[0].text.split())
        # 店铺名称
        dct['shop_name'] = item.select('div.p-shop')[0].text
        # 商品链接
        dct['product_link'] = base_url + item.select('div.p-name.p-name-type-2 a')[0].get('href')
        try:
            # 店铺链接
            dct['shop_link'] = base_url + item.select('div.p-shop a')[0].get('href')
        except:
            dct['shop_link'] = ''
        # 商品id
        dct['product_id'] = item.select('div.p-name.p-name-type-2 i')[0].get('id').split('_')[-1]
        id_lst.append(dct['product_id'])
        print(dct)
    for i in id_lst:
        get_comments(i)


# 解析json地址
def get_data(url):
    res = requests.get(url, headers=headers, proxies=proxy.get_proxy(proxies)[-1], verify=False)
    text = re.findall('\{.*\}', res.text)
    data = json.loads(text[0])
    for item in data['comments']:
        dct_comments = {}
        # 评论人
        dct_comments['username'] = item['nickname']
        # 评论人ID
        dct_comments['id'] = item['id']
        # 评论型号
        dct_comments['model'] = item['productSize']
        # 评论内容
        dct_comments['content'] = item['content']
        # 评论时间
        dct_comments['date'] = item['creationTime']
        # 点赞数量
        dct_comments['like'] = item['usefulVoteCount']
        print(dct_comments)
    headers['Referer'] = url
    return True


# 获取前10页数据
def get_comments(product_id):
    """
    也可根据详情页链接，提取商品id进行抓取，详情页地址例如
    https://item.jd.com/8638898.html?jd_pop=2babb2c8-9b31-45ba-b0d2-54d0235259a4&abt=0
    """
    base_url = 'https://sclub.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98vv2748&productId={}&score=0&sortType=5&page={}&pageSize=10&isShadowSku=0&rid=0&fold=1'
    url_lst = [base_url.format(product_id, x) for x in range(1, 10)]
    for url in url_lst:
        get_data(url)
        time.sleep(random.uniform(3, 6))


def go():
    qw = get_qw()
    base_url = 'https://search.jd.com/Search?keyword={}&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq={}&page={}&s=1&click=1'
    url_lst = [base_url.format(qw, qw, x) for x in range(1, 7)]
    for url in url_lst:
        get_product_id(url)
        time.sleep(random.uniform(3, 6))


if __name__ == '__main__':
    go()
    # get_comments(3459483)
    # get_data(
    #     'https://sclub.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98vv2748&productId=8776186&score=0&sortType=5&page=2&pageSize=10&isShadowSku=0&rid=0&fold=1')
    # get_product_id(start_url)