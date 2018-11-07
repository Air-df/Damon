import re
import time
import json
import random
import itchat
import requests
import datetime
import threading
import traceback
import pymysql

from plugins import proxy, time_now
from faker import Factory
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

"""
# 评论数据API
# 非登录状态下只能查看
"""

HEADERS = {
    'User-Agent': Factory().create().user_agent(),
    'Referer': 'https://m.weibo.cn/'
}
COUNT = 1
# 设置爬取页数
page_end = 50
# 间隔时间（分）
frequence = 10

# 无效数据数量
gabage_num = 0
# 断开条件--无效数据最大量
limit_num = 1000
# 有效期----格式示例：2018-11-11
start_time = '2018-10-27'
dead_time = '2018-10-29'
# 是否启用有效期
switch = True
search_keyword = '飞利浦 电动牙刷'
media_type = '微博'
media_name = '新浪微博'
proxies = proxy.get_proxies()
start_url = 'https://m.weibo.cn/search?containerid=231583'
#   mysql配置
mysql = {
    'host': '114.55.96.174',
    'port': 3306,
    'user': 'root',
    'password': 'Beats1111',
    'db': 'beats',
    'charset': 'utf8'
}
conn = pymysql.connect(**mysql)
cursor = conn.cursor()
execute = cursor.execute

"""
api
https://m.weibo.cn/api/container/getIndex?containerid=100103type%3D1%26q%3D%E4%B8%8A%E6%B5%B7&page_type=searchall&page=1
"""


# 获取containerid
def get_containerid():
    while 1:
        try:
            service_args = [
                '--proxy={}'.format(proxy.get_proxy(proxies)[-1]),  # 代理http://IP:PORT 只设置该项也可以
                '--load-images=no',  # 图片加载开关
                '--disk-cache=yes',  # 缓存控制
                '--ignore-ssl-errors=true',  # 忽略ssl错误
            ]
            driver = webdriver.PhantomJS(service_args=service_args)
            driver.get(start_url)
            driver.find_element_by_tag_name('input').send_keys(search_keyword)
            driver.find_element_by_tag_name('input').send_keys(Keys.ENTER)
            time.sleep(2)
            driver.find_element_by_xpath('//*[@id="app"]/div[1]/div[1]/div[2]/div[2]/div[1]/div/div[1]/div/ul/li[3]/span').send_keys(Keys.ENTER)
            time.sleep(2)
            url = driver.current_url
            driver.close()
            print(url.split('?')[-1])
            return url.split('?')[-1]
        except:
            traceback.print_exc()
            continue


# 数据存储
def write_to_mysql(**kwargs):
    global conn
    execute('select weibo_id from weibo')
    result = cursor.fetchall()
    if (kwargs['weibo_id'], ) not in result:
        execute(
            'insert into weibo(\
            media_type, \
            media_name, \
            create_time, \
            title, \
            link, \
            isoriginal, \
            user_name, \
            original, \
            keyword, \
            reports_count,\
            comment_count,\
            attitude_count, \
            followers_count, \
            weibo_id, \
            user_link) values ("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}")'.format(
                kwargs['media_type'],
                kwargs['media_name'],
                kwargs['create_time'],
                kwargs['title'],
                kwargs['weibo_link'],
                kwargs['isoriginal'],
                kwargs['user_name'],
                kwargs['original'],
                kwargs['keyword'],
                kwargs['reports_count'],
                kwargs['comment_count'],
                kwargs['attitude_count'],
                kwargs['followers_count'],
                kwargs['weibo_id'],
                kwargs['user_link']
            ))
        conn.commit()


# 解析json
def get_info(url):
    global COUNT, gabage_num
    response = requests.get(url, headers=HEADERS, proxies=proxy.get_proxy(proxies)[-1], verify=False)
    response.encoding = 'utf-8'
    data = json.loads(response.text)
    cards = [x['card_group'] for x in data['data']['cards']]
    # 解析json数据
    for card in cards:
        for blog in card:
            dct = {}
            dct['media_type'] = media_type
            dct['media_name'] = media_name
            try:
                title_html = blog['mblog']['text']
                soup = BeautifulSoup(title_html, 'lxml')
                # 微博名称
                regex = re.compile(r'[\u4e00-\u9fa5@#,，\.。！/~？\?]+')
                title = '，'.join(regex.findall(soup.text))
                dct['title'] = title
                # 微博ID
                dct['weibo_id'] = blog['mblog']['id']
                # 创建时间
                create_time = blog['mblog']['created_at']
                # now = ':'.join(str(datetime.datetime.now()).split('.')[0].split(':')[:-1:])
                if ('前' in create_time) or ('天' in create_time):
                     create_time = time_now.make_time(create_time)
                     dct['create_time'] = time_now.check_date(create_time, start_time, dead_time)
                elif switch:
                    check_result = time_now.check_date(create_time, start_time, dead_time)
                    print(check_result)
                    if check_result:
                        dct['create_time'] = check_result
                    else:
                        gabage_num += 1
                        if gabage_num > limit_num:
                            return True
                        else:
                            continue
                else:
                    gabage_num += 1
                    if gabage_num > limit_num:
                        print('gabage_num', gabage_num)
                        return True
                    else:
                        continue
                    # pass
                # 博主名称
                dct['user_name'] = blog['mblog']['user']['screen_name']
                # 博主粉丝数
                dct['followers_count'] = blog['mblog']['user']['followers_count']
                # 评论数
                dct['comment_count'] = blog['mblog']['comments_count']
                # 点赞数
                dct['attitude_count'] = blog['mblog']['attitudes_count']
                # 转发数
                dct['reports_count'] = blog['mblog']['reposts_count']
                dct['keyword'] = search_keyword
                # 微博链接
                dct['weibo_link'] = 'https://m.weibo.cn/detail/' + dct['weibo_id']
            except:
                # traceback.print_exc()
                # print(blog)
                continue
            try:
                # 博主链接
                dct['user_link'] = blog['mblog']['user']['profile_url']
            except:
                traceback.print_exc()
                dct['user_link'] = ''
                # print(blog)
            try:
                # 微博图片链接
                dct['pic_link'] = blog['mblog']['bmiddle_pic']
            except:
                # traceback.print_exc()
                dct['pic_link'] = ''
            try:
                # 原创内容
                html = blog['mblog']['retweeted_status']['text']
                soup = BeautifulSoup(html, 'lxml')
                dct['original'] = soup.text
                # 是否为原创
                dct['isoriginal'] = '转发'
            except:
                dct['original'] = ''
                dct['isoriginal'] = '原创'
            try:
                write_to_mysql(**dct)
                # print('第{}条微博'.format(COUNT))
                # COUNT += 1
            except:
                traceback.print_exc()
                # print(url)
                # print(dct)
                pass
            for i in dct:
                print('{}: {}'.format(i, dct[i]))
            print('我是分割线'.center(150, '*'))
    HEADERS['Referer'] = url


def go():
    global gabage_num
    try:
        container_id = get_containerid()
    except:
        container_id = get_containerid()
    count = 1
    while 1:
        try:
            start_time = int(time.time())
            url = 'https://m.weibo.cn/api/container/getIndex?{}&page_type=searchall&page='.format(container_id)
            urls = [url + str(page) for page in range(1, page_end)]
            for link in urls:
                time.sleep(random.uniform(3, 5))
                if get_info(link):
                    break
            gabage_num = 0
            end_time = int(time.time())
            run_time = end_time - start_time
            if run_time < frequence*60:
                print('课间五分钟%d次' % count)
                count += 1
                time.sleep(frequence*60 - run_time)
        except:
            traceback.print_exc()
            break
            # go()


if __name__ == '__main__':
    go()
    # get_containerid()
