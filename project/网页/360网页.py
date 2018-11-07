import re
import time
import random
import traceback
import requests
import pymysql

from bs4 import BeautifulSoup
from faker import Factory
from plugins import proxy, time_now
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains


# 页数
page_num = 2
# 搜索关键字，对应参数--wd、op
search_keyword = '天梭'
media_type = '网页'
media_name = '360搜索'
"""
搜索时间,对应字母 
一天  d
一周  w
一月  m
"""
search_type = 'd'
proxies = proxy.get_proxies()
# 基础链接
base_url = 'https://www.so.com'
url = 'https://www.so.com/s?ie=utf-8&fr=sidenav_www&src=home_suggst_test&q={}&eci=&nlpv=&adv_t={}'.format(search_keyword, search_type)
headers = {
    'User-Agent': Factory().create().user_agent(),
    'Referer': 'https://www.so.com/?src=sidenav_www'
}
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


def get_url_by_selenium(url):
    proxies = proxy.get_proxies()
    service_args = [
        '--proxy={}'.format(proxy.get_proxy(proxies)[-1]),  # 代理http://IP:PORT 只设置该项也可以
        '--load-images=no',  # 图片加载开关
        '--disk-cache=yes',  # 缓存控制
        '--ignore-ssl-errors=true',  # 忽略ssl错误
    ]
    driver = webdriver.PhantomJS(service_args=service_args)
    driver.get(url)
    time.sleep(1)
    driver.find_element_by_id('input').send_keys(search_keyword)
    driver.find_element_by_id('search-button').click()
    time.sleep(random.uniform(1, 3))
    # 找到设置按钮
    tag = driver.find_element_by_xpath('//*[@id="hd-rtools"]/div/div[3]/a')
    ActionChains(driver).move_to_element(tag).perform()
    tag_set = driver.find_element_by_xpath('//*[@id="search_setting"]/a')
    ActionChains(driver).move_to_element(tag_set).click()
    time.sleep(2)
    # driver.find_element_by_xpath('//*[@id="adv-search"]/a[{}]'.format(search_type)).click()
    # time.sleep(random.uniform(1, 3))
    driver.save_screenshot('一天内.png')
    url = driver.current_url
    html = driver.page_source
    driver.close()
    print(url)
    # print(html)
    return html


def get_url_by_requests(url):
    res = requests.get(url)
    html = res.text
    soup = BeautifulSoup(html, 'lxml')
    psid = soup.select('input[name="psid"]')[0].get('value')
    return psid


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


def get_data(url):
    global page_num
    res = requests.get(url, headers=headers, proxies=proxy.get_proxy(proxies)[-1], verify=False)
    html = res.text
    soup = BeautifulSoup(html, 'lxml')
    for item in soup.select('li.res-list'):
        dct = {}
        dct['media_type'] = media_type
        dct['media_name'] = media_name
        # 标题
        try:
            # 标题
            dct['title'] = item.select('h3 a')[0].text
            # 时间
            dct['create_time'] = item.select('span.gray')[0].text
            # 链接
            link = item.select('h3 a')[0].get('href')
            dct['link'] = link
            # 概要
            dct['brief'] = re.sub(r'\n|\xa0|  |\t', '', item.select('div')[0].text)
        except:
            continue
        try:
            # 发布媒体
            dct['resource_from'] = item.select('p.res-linkinfo > a')[-1].text
        except:
            dct['resource_from'] = ''
        print(dct)
    # 下一页链接
    try:
        next_page = soup.select('a#snext')[0].get('href')
        next_page_url = base_url + next_page
        print('第{}页'.format(page_num), next_page_url, sep='\n')
        time.sleep(random.uniform(2, 5))
        page_num += 1
        get_data(next_page_url)
    except Exception as e:
        traceback.print_exc()
        print('end')


if __name__ == '__main__':
    get_data(url)
    # get_url_by_selenium(base_url)
