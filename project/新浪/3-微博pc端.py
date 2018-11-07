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

from plugins import proxy, num, time_now
from faker import Factory
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

"""
搜索主页----》搜索关键字----》搜索时间筛选-----》遍历页数----》获取相关字段  二级页面地址
一级页面可抓取字段
    发布时间 内容摘要
"""

HEADERS = {
    'User-Agent': Factory().create().user_agent(),
    'Referer': 'https://s.weibo.com/'
}
# 设置爬取页数
page_end = 50
# 间隔时间（分）
frequence = 10
# 有效期
# 是否启用有效期(默认起始时间为当前时间的前一小时）
switch = False
# 起始时间
start_year = 2018
start_month = 11
start_day = 1
start_hour = 1
start_time = "{}-{}-{}-{}".format(start_year, start_month, start_day, start_hour)
# 结束时间（默认为当日的23时）
end_year = 2018
end_month = 11
end_day = 2
end_hour = 23
end_time = "{}-{}-{}-{}".format(end_year, end_month, end_day, end_hour)
# 重复信息数量
gabage_num = 1
# 重复信息数量最大值---超过该值则中断爬取
limit_num = 50
search_keyword = '娱乐'
media_type = '微博'
media_name = '新浪微博'
proxies = proxy.get_proxies()
start_url = 'https://s.weibo.com/weibo?q={}&Refer=index'.format(search_keyword)
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


def get_containerid_by_request():
    while 1:
        try:
            res = requests.get(start_url, headers=HEADERS, proxies=proxy.get_proxy(proxies)[-1])
            url = res.url
            print(url.split('?')[-1].split('&')[0])
            HEADERS['Referer'] = url
            return url.split('?')[-1].split('&')[0]
        except:
            traceback.print_exc()
            time.sleep(random.uniform(3, 10))
            continue


# ok
def write_to_mysql(**kwargs):
    """
    数据存储
    :param kwargs:
    :return: none
    """
    global conn
    execute('select link from weibo')
    result = cursor.fetchall()
    if (kwargs['weibo_link'],) not in result:
        execute(
            'insert into weibo(\
            media_type, \
            media_name, \
            create_time, \
            title, \
            link, \
            pub_type, \
            user_name, \
            user_type, \
            reports_count, \
            comment_count, \
            attitude_count, \
            isoriginal, \
            original_create_time, \
            original_link, \
            original_user_name, \
            original_user_type, \
            original_reports_count, \
            original_comment_count, \
            original_attitude_count, \
            keyword) values ("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}")'.format(
                kwargs['media_type'],
                kwargs['media_name'],
                kwargs['create_time'],
                kwargs['title'],
                kwargs['weibo_link'],
                kwargs['pub_type'],
                kwargs['user_name'],
                kwargs['user_type'],
                kwargs['reports_count'],
                kwargs['comment_count'],
                kwargs['attitude_count'],
                kwargs['isoriginal'],
                kwargs['original_create_time'],
                kwargs['original_link'],
                kwargs['original_user_name'],
                kwargs['original_user_type'],
                kwargs['original_reports_count'],
                kwargs['original_comment_count'],
                kwargs['original_attitude_count'],
                kwargs['keyword']
            ))
        conn.commit()
    else:
        link_new = kwargs['weibo_link']
        execute('select link from weibo where link="{}"'.format(link_new))
        link_old = cursor.fetchall()[0][0]
        print('已有链接：', link_old)
        print('新链接：', link_new)
        return True


# ok
def get_info(url):
    """
    解析对应网页，并写入数据库
    """
    global gabage_num
    res = requests.get(url, headers=HEADERS, proxies=proxy.get_proxy(proxies)[-1])
    html = res.text
    soup = BeautifulSoup(html, 'lxml')
    items = soup.select('div[action-type="feed_list_item"]')
    if len(items) == 0:
        # print(url)
        return True
    try:
        for item in items:
            base_url = 'https:'
            try:
                dct = {}
                dct['media_type'] = media_type
                dct['media_name'] = media_name
                dct['keyword'] = search_keyword
                # 发布时间
                dct['create_time'] = time_now.make_time_for_pc(
                    ' '.join(item.select('div.content > p.from > a')[0].text.split()))
                # 内容概要
                dct['title'] = ''.join(item.select('p[node-type="feed_list_content"]')[0].text.split())
                # 微博链接
                dct['weibo_link'] = base_url + item.select('div.content > p.from > a')[0].get('href')
                # 发布平台
                dct['pub_type'] = item.select('div.content > p.from > a')[1].text
                # 发布者
                dct['user_name'] = ''.join(item.select('div.info')[0].text.split()).replace('@', '')
                # 发布者认证类型
                tag_a_list = item.select('div.info > div')[1].select('a')
                tag_a_num = len(tag_a_list)
                if tag_a_num == 2:
                    dct['user_type'] = tag_a_list[-1].get('title').replace('微博', '')
                else:
                    dct['user_type'] = ''
                # 转发数
                dct['reports_count'] = num.check_num(item.select('div.card-act a')[1].text)
                # 评论数
                dct['comment_count'] = num.check_num(item.select('div.card-act a')[2].text)
                # 点赞数
                dct['attitude_count'] = num.check_num(item.select('div.card-act a')[3].text)
                # 收藏数
                dct['collection_count'] = num.check_num(item.select('div.card-act a')[0].text)
                try:
                    # 是否原创
                    dct['isoriginal'] = '0'
                    # 原创内容
                    dct['original_content'] = item.select('div[node-type="feed_list_forwardContent"] > p[node-type="feed_list_content"]')[0].text
                    # 原微博链接
                    dct['original_link'] = base_url + item.select('div.func > p.from > a')[0].get('href')
                    # 原博主
                    dct['original_user_name'] = item.select('div[node-type="feed_list_forwardContent"] > a')[
                        0].text.replace('@', '')
                    # 原博主认证类型
                    original_tag_a_lst = item.select('div[node-type="feed_list_forwardContent"] > a')
                    if len(original_tag_a_lst) != 1:
                        dct['original_user_type'] = original_tag_a_lst[1].get('title').replace('微博', '')
                    else:
                        dct['original_user_type'] = ''
                    # 原微博发布时间
                    dct['original_create_time'] = time_now.make_time_for_pc(
                        item.select('div.func > p.from > a')[0].text)
                    # 原微博发布平台
                    dct['original_pub_type'] = item.select('div.func > p.from > a')[1].text
                    # 原微博转发数
                    dct['original_reports_count'] = num.check_num(item.select('ul.act.s-fr a')[0].text)
                    # 原微博评论数
                    dct['original_comment_count'] = num.check_num(item.select('ul.act.s-fr a')[1].text)
                    # 原微博点赞数
                    dct['original_attitude_count'] = num.check_num(item.select('ul.act.s-fr a')[2].text)
                except:
                    # traceback.print_exc()
                    dct['isoriginal'] = '1'
                    dct['original_create_time'] = ''
                    dct['original_link'] = ''
                    dct['original_user_name'] = ''
                    dct['original_user_type'] = ''
                    dct['original_reports_count'] = 0
                    dct['original_comment_count'] = 0
                    dct['original_attitude_count'] = 0
                try:
                    result = write_to_mysql(**dct)
                    # print(dct)
                    if result:
                        # return True
                        gabage_num += 1
                        if gabage_num > limit_num:
                            # return True
                            pass
                except pymysql.err.InternalError:
                    regex = re.compile(r'[\u4e00-\u9fa5@#,，\.。！/~？\?]+')
                    title = '，'.join(regex.findall(soup.text))
                    dct['title'] = title
                    write_to_mysql(**dct)
                else:
                    pass
            except:
                traceback.print_exc()
    except:
        traceback.print_exc()
    HEADERS['Referer'] = url


def go():
    global start_time, end_time
    try:
        container_id = get_containerid_by_request()
    except:
        container_id = get_containerid_by_request()
    count = 1
    while 1:
        if not switch:
            now = datetime.datetime.now()
            date = str(now.date()).split('-')
            now = str(now.time()).split('.')[0].split(':')
            end_year = int(date[0])
            end_month = int(date[1])
            end_day = int(date[2])
            end_time = '{}-{}-{}'.format(end_year, end_month, end_day)
            start_time = time_now.make_time_for_pc('1小时前')
            start_year = start_time.split()[0].split('-')[0]
            start_month = start_time.split()[0].split('-')[1]
            start_day = start_time.split()[0].split('-')[2]
            start_hour = start_time.split()[1].split(':')[0]
            start_time = '{}-{}-{}-{}'.format(start_year, start_month, start_day, start_hour)
            url = 'https://s.weibo.com/weibo?&{}&typeall=1&suball=1&timescope=custom:{}&Refer=g&page='.format(
                container_id, start_time)
            urls = ['https://s.weibo.com/weibo?&{}&typeall=1&suball=1&timescope=custom:{}&Refer=g'.format(container_id,
                                                                                                          start_time)]
            urls.extend([url + str(page) for page in range(2, page_end)])
        else:
            url = 'https://s.weibo.com/weibo?&{}&typeall=1&suball=1&timescope=custom:{}:{}&Refer=g&page='.format(
                container_id, start_time, end_time)
            urls = ['https://s.weibo.com/weibo?&{}&typeall=1&suball=1&timescope=custom:{}:{}&Refer=g'.format(container_id, start_time, end_time)]
            urls.extend([url + str(page) for page in range(2, page_end)])
        try:
            start = int(time.time())
            for link in urls:
                time.sleep(random.uniform(3, 5))
                print(link)
                if get_info(link):
                    break
            end = int(time.time())
            run_time = end - start
            if run_time < frequence * 60:
                print('%d次' % count)
                count += 1
                time.sleep(frequence * 60 - run_time)
        except:
            traceback.print_exc()
            break


if __name__ == '__main__':
    # url = 'https://s.weibo.com/weibo?&q=%E9%A3%9E%E5%88%A9%E6%B5%A6%20%E5%89%83%E9%A1%BB%E5%88%80&typeall=1&suball=1&timescope=custom:2018-11-06-21:2018-11-6&Refer=g&page=2'
    # print(get_info(url))
    go()
