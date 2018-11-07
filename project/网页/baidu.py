import re
import time
import requests
import traceback

from bs4 import BeautifulSoup
from faker import Factory
from plugins import proxy

proxies = proxy.get_proxies()
# 页数
page_num = 1
# 搜索关键字，对应参数--wd、op
search_keyword = ''
# 有效时间
search_time = ['一天', '一周', '一月', '一年']
# # 文件类型
# file_type = ['pdf', 'doc', 'xls', 'ppt', 'rtf']
# # 站点查询
# search_in_site = 'douban.com'

url = 'https://www.baidu.com/s?wd=%E7%AC%94%E8%AE%B0%E6%9C%AC&pn=10&oq=%E7%AC%94%E8%AE%B0%E6%9C%AC&ie=utf-8&usm=5&rsv_idx=1&rsv_pq=9b80529f000560e5&rsv_t=f741Th10t2O9Tl9h70TkgSVZc%2F5BqWbeCYZMC%2BR4WGDwPYPIlZjTrQHMe0Y'
headers = {
    'User-Agent': Factory().create().user_agent(),
    # 'User-Agent': 'Googlebot',
    'Referer': 'http://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&tn=92319197_hao_pg&wd=%E5%BD%B1%E8%AF%84&ct=2097152&si=douban.com&oq=%25E6%2597%25A0%25E5%258F%258C&rsv_pq=d1962b1e0007dd9a&rsv_t=e8effJGmC32yCMgaG4cTslI0sOgVLZKislpDjSJUprSc1u8hXMyO%2Fki7cPMhlzXr3ma2gNoz&rqlang=cn&rsv_enter=0&rsv_sug3=8&rsv_sug1=8&rsv_sug7=100&bs=%E6%97%A0%E5%8F%8C'
}


def get_data(url):
    global page_num
    keyword = '笔记本'
    res = requests.get(url, proxies=proxy.get_proxy(proxies)[-1], headers=headers, verify=False)
    html = res.text
    soup = BeautifulSoup(html, 'lxml')
    for item in soup.select('div.result.c-container'):
        dct = {}
        # 标题
        dct['title'] = keyword + item.select('h3 a')[0].text.replace('<em>', '').replace('</em>', '')
        # 概要
        try:
            dct['brief'] = re.sub(r'<\w*>|</\w*>|\xa0-\xa0', '', item.select('div.c-abstract')[0].text)
        except:
            dct['brief'] = 'null'
        # 发布时间
        try:
            dct['date'] = re.sub('\xa0-\xa0', '', item.select('div.c-abstract span')[0].text)
        except:
            dct['date'] = 'null'
        # 发布媒体
        # 链接
        dct['link'] = item.select('h3 a')[0].get('href')

        print(dct)
    # 下一页链接
    try:
        next_page = soup.select('div#page > a')[0].get('href')
        headers['Referer'] = url
        page_num += 1
        next_page_url = 'http://www.baidu.com/s?wd=%E6%97%A0%E5%8F%8C&pn={}&oq=%E6%97%A0%E5%8F%8C&tn=92319197_hao_pg&ie=utf-8&usm=2&rsv_pq=cbeb180a0009e803&rsv_t=e865s49G3vYyfwnQmCzx7eJo41Bj49Ui%2Bay03YHeZw%2BjB0FoQTm1qV4qI24PaI9xk6vjQKdg'.format(
            10 * page_num)

        print('开始下一页', next_page_url)
        get_data(next_page_url)
    except Exception as e:
        traceback.print_exc()
        print('end')


def loop():
    while 1:
        get_data(url)
        time.sleep(7200)


if __name__ == '__main__':
    loop()
