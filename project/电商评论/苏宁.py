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
搜索页为js加载
链接地址示例：
热水器商品链接
https://search.suning.com/emall/searchV1Product.do?keyword={}&ci=20344&pg=01&cp=0&il=0&st=0&iy=0&isDoufu=1&n=1&sesab=ACAABAAB&id=IDENTIFYING&cc=021&paging=1&sub=0&jzq=8999
手机商品链接
https://search.suning.com/emall/searchV1Product.do?keyword={}&ci=0&pg=01&cp=0&il=0&st=0&iy=0&n=1&sesab=ACAABAAB&id=IDENTIFYING&cc=021&paging=2&sub=1&jzq=1149537
keyword 为关键字
jzq     关键字对应的编号    隐藏在搜索第一页中的form中<input type="hidden" value="127265" id="totalCount">
paging  页数
ci      参数在变化，但是对结果没有影响
价格信息为单独请求，链接示例
https://ds.suning.cn/ds/generalForTile/000000010570982448_,000000010591250994_,000000000123129118_,000000010585219083_,000000010598445412_,000000000945031943_,000000000945031936_-021-2-0000000000-1--ds0000000003480.jsonp?callback=ds0000000003480

评论链接
https://review.suning.com/ajax/cluster_review_lists/general-30193812-000000010606649858-0000000000-total-2-default-10-----reviewList.htm?callback=reviewList

"""
headers = {
    'User-Agent': Factory().create().user_agent(),
    'Referer': 'https://www.suning.com/'
}
proxies = proxy.get_proxies()
search_keyword = input('输入关键字')
start_url = 'https://search.suning.com/{}/'.format(search_keyword)


def get_qw():
    res = requests.get(start_url, headers=headers, proxies=proxy.get_proxy(proxies)[-1], verify=False)
    html = res.text
    qw = res.url.split('/')[-2]
    soup = BeautifulSoup(html, 'lxml')
    jzq = soup.select('input#totalCount')[0].get('value')
    return (qw, jzq)


# 解析搜索结果
def get_product_id(url):
    res = requests.res = requests.get(url, headers=headers, proxies=proxy.get_proxy(proxies)[-1], verify=False)
    # res.encoding = 'utf-8'
    html = res.text
    # print(html)
    soup = BeautifulSoup(html, 'lxml')
    base_url = 'https:'
    id_lst = []
    for item in soup.select('div.product-box'):
        dct = {}
        # 商品名称
        dct['product_name'] = ''.join(item.select('div.title-selling-point a')[0].text.split())
        # 商品价格
        # dct['price'] = item.select('div.p-price i')[0].text
        try:
            # 评论数量
            dct['comment_account'] = item.select('div.info-evaluate i')[0].text
        except:
            dct['comment_account'] = ''
        # 店铺名称
        dct['shop_name'] = item.select('div.store-stock')[0].text
        # 商品链接
        dct['product_link'] = base_url + item.select('div.title-selling-point a')[0].get('href')
        # 店铺链接
        link = item.select('div.store-stock a')[0].get('href')
        if 'java' in link:
            dct['shop_link'] = '苏宁自营'
        else:
            dct['shop_link'] = base_url + link
        # 商品id
        dct['product_id'] = dct['product_link'].split('/')[-1].split('.')[0]
        id_lst.append(dct['product_id'])
        print(dct)
    for i in id_lst:
        get_comments(i)


# 解析json地址
def get_data(url):
    res = requests.get(url, headers=headers, proxies=proxy.get_proxy(proxies)[-1], verify=False)
    text = re.findall('\{.*\}', res.text)
    data = json.loads(text[0])
    for item in data['commodityReviews']:
        dct_comments = {}
        # 评论人
        dct_comments['username'] = item['userInfo']['nickName']
        # 评论人ID
        dct_comments['id'] = item['userInfo']['levelId']
        # 评论型号
        dct_comments['model'] = item['commodityInfo']['commodityName']
        # 评论内容
        dct_comments['content'] = item['content']
        try:
            # 评论关键字
            dct_comments['keywords'] = [x['labelName'] for x in item['labelNames']]
            dct_comments['like'] = item['usefulCnt']
        except:
            dct_comments['keywords'] = ''
            # 点赞数量
            dct_comments['like'] = ''
        # 评论时间
        dct_comments['date'] = item['publishTime']
        print(dct_comments)
    headers['Referer'] = url
    return True


# 获取前10页数据
def get_comments(product_id):
    """
    也可根据详情页链接，提取商品id进行抓取，详情页地址例如
    https://item.jd.com/8638898.html?jd_pop=2babb2c8-9b31-45ba-b0d2-54d0235259a4&abt=0
    """
    base_url = 'https://review.suning.com/ajax/cluster_review_lists/general-30193812-0000000{}-0000000000-total-{}-default-10-----reviewList.htm?callback=reviewList'
    url_lst = [base_url.format(product_id, x) for x in range(1, 10)]
    for url in url_lst:
        get_data(url)
        time.sleep(random.uniform(3, 6))


def go():
    qw, jzq = get_qw()
    base_url = 'https://search.suning.com/emall/searchV1Product.do?keyword={}&ci=0&pg=01&cp=0&il=0&st=0&iy=0&n=1&sesab=ACAABAAB&id=IDENTIFYING&cc=021&paging={}&sub=1&jzq={}'
    url_lst = [base_url.format(qw, x, jzq) for x in range(1, 7)]
    for url in url_lst:
        get_product_id(url)
        time.sleep(random.uniform(3, 6))


if __name__ == '__main__':
    go()
    # get_comments(3459483)
    # get_data('https://review.suning.com/ajax/cluster_review_lists/general-30193812-000000010606649858-0000000000-total-3-default-10-----reviewList.htm?callback=reviewList')
    # get_product_id(start_url)
    # print(get_qw())
