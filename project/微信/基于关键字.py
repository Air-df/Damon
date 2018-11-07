import re
import time
import random
import traceback
import pymysql

from bs4 import BeautifulSoup
from selenium import webdriver
from plugins import proxy, time_now

# 页数
page_num = 1
page_end = 50
gabage_num = 0
# 间隔时间（分）
frequence = 5
# 运行次数
count = 1
# 无效信息上限
limit_num = 50
# 搜索关键字
search_keyword = '飞利浦电动牙刷'
media_type = '微信'
media_name = '微信'
start_url = 'http://weixin.sogou.com/'
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
proxies = proxy.get_proxies()
service_args = [
        '--proxy={}'.format(proxy.get_proxy(proxies)[-1]),  # 代理http://IP:PORT 只设置该项也可以
        '--load-images=no',  # 图片加载开关
        '--disk-cache=yes',  # 缓存控制
        '--ignore-ssl-errors=true',  # 忽略ssl错误
    ]
driver = webdriver.PhantomJS(service_args=service_args)
driver.get(start_url)


def get_html():
    global gabage_num
    gabage_num = 0
    driver.find_element_by_id('query').send_keys(search_keyword)
    driver.find_element_by_css_selector('input[uigs="search_article"]').click()
    time.sleep(2)
    driver.find_element_by_css_selector('div#tool_show > a').click()
    driver.find_element_by_id('time').click()
    driver.find_element_by_css_selector('a[uigs="select_time_day"]').click()
    time.sleep(2)
    # print(driver.page_source)
    for page in range(1, page_end):
        html = driver.page_source
        url = driver.current_url
        # print(url)
        if parse(html):
            return
        try:
            driver.find_element_by_id('sogou_next').click()
            time.sleep(random.uniform(3, 5))
        except:
            break


# 数据存储
def write_to_mysql(**kwargs):
    global conn, gabage_num
    execute('select create_time, user_name from wechat')
    result = cursor.fetchall()
    if (kwargs['create_time'], kwargs['user_name'],) not in result:
        execute(
            'insert into wechat(\
            media_type, \
            media_name, \
            create_time, \
            title, \
            link, \
            user_name, \
            keyword) values ("{}", "{}", "{}", "{}", "{}", "{}", "{}")'.format(
                kwargs['media_type'],
                kwargs['media_name'],
                kwargs['create_time'],
                kwargs['title'],
                kwargs['link'],
                kwargs['user_name'],
                kwargs['keyword'],
            ))
        conn.commit()
        return 0
    else:
        gabage_num += 1
        return gabage_num


def parse(html):
    # print(html)
    soup = BeautifulSoup(html, 'lxml')
    for item in soup.select('div.txt-box'):
        dct = {}
        # 媒体类型
        dct['media_type'] = media_type
        # 媒体名称
        dct['media_name'] = media_name
        # 发布日期
        create_time = item.select('div.s-p')[0].get('t')
        dct['create_time'] = time_now.transform_unix(create_time)
        # 标题
        dct['title'] = item.select('a')[0].text
        # 地址
        dct['link'] = item.select('a')[0].get('href')
        # 昵称
        dct['user_name'] = item.select('a')[1].text
        # 关键词
        dct['keyword'] = search_keyword
        is_in = write_to_mysql(**dct)
        if is_in > limit_num:
            return True
        # for i in dct:
        #     print('{}: {}'.format(i, dct[i]))
        # print('我是分割线'.center(150, '*'))


def go():
    global count
    while 1:
        try:
            start_time = int(time.time())
            get_html()
            end_time = int(time.time())
            run_time = end_time - start_time
            if run_time < frequence * 60:
                print('课间五分钟%d次' % count)
                count += 1
                time.sleep(frequence * 60 - run_time)
        except:
            traceback.print_exc()
            continue


if __name__ == '__main__':
    # get_data(url)
    # get_html()
    # driver.close()
    go()
