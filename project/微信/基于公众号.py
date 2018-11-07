import re
import time
import random
import requests
import pymysql

from plugins import proxy

proxies = proxy.get_proxies()

"""
抓取速度过快  账号会被限
需更新headers、start_url信息
"""
# 微信读书公众号
start_url = 'https://mp.weixin.qq.com/mp/profile_ext?action=getmsg&__biz=MzA3MzQ4NDIzNw==&f=json&offset=10&count=10&is_ok=1&scene=126&uin=777&key=777&pass_ticket=UZHjOXfnq3fcxU72z1JYsNlcD6xr9Vjd9yAIDoKadkg2BSLyQHjiKVhm2TSALOQS&wxtoken=&appmsg_token=981_3NZL%252BfeS5NeCjC3xJEnZtpzCTtb5lWs5J5BM3g~~&x5=0&f=json HTTP/1.1'
num = 1
page_end = 50
headers = """Host: mp.weixin.qq.com
Accept-Encoding: br, gzip, deflate
Cookie: devicetype=iOS12.0.1; lang=zh_CN; pass_ticket=UZHjOXfnq3fcxU72z1JYsNlcD6xr9Vjd9yAIDoKadkg2BSLyQHjiKVhm2TSALOQS; version=16070322; wap_sid2=CMW4uKEGElxGY2FwaWlnMkVnUTJQeVV1SnlrdktVS0wta1BveFY3MGNEVDhQZW1ESnlxekxZZl9jTjlRRjVjYUh2SWtCV0NFRVh5bE1LaG4zVlViY2RWRFVITGZwTlVEQUFBfjDuvoDfBTgNQJVO; wxuin=1680743493
Connection: keep-alive
Accept: */*
User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 12_0_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16A404 MicroMessenger/6.7.3(0x16070321) NetType/WIFI Language/zh_CN
Referer: https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=MzA3MzQ4NDIzNw==&scene=126&subscene=0&devicetype=iOS12.0.1&version=16070322&lang=zh_CN&nettype=WIFI&a8scene=0&fontScale=100&pass_ticket=UZHjOXfnq3fcxU72z1JYsNlcD6xr9Vjd9yAIDoKadkg2BSLyQHjiKVhm2TSALOQS&wx_header=1
Accept-Language: zh-cn
X-Requested-With: XMLHttpRequest"""

headers = {each.split(':', 1)[0]: each.split(':', 1)[1].replace(' ', '', 1) for each in headers.split('\n')}

"""
# 微信读书公众号
url = 'https://mp.weixin.qq.com/mp/profile_ext?action=getmsg&__biz=MzA5OTE5NTI5Mw==&f=json&offset=30&count=10&is_ok=1&scene=126&uin=777&key=777&pass_ticket=3qs3teMjvUrLPRZENHgssvM1e03UYDbmH1sR0825XQM%3D&wxtoken=&appmsg_token=971_nNeS0vNGtOZZ2VyoK5wi4PTfX9lKL7dTu55ZoA~~&x5=0&f=json'
# 建设银行
url = 'https://mp.weixin.qq.com/mp/profile_ext?action=getmsg&__biz=MjM5MTA4Mzc2MQ==&f=json&offset=10&count=10&is_ok=1&scene=126&uin=777&key=777&pass_ticket=%2FVj1u58888qnsOsVRuDT7uMjTWFRhE7Rrhzjb2SBlzo%3D&wxtoken=&appmsg_token=980_m6nAE3HZCf09G9liUWA1YXUQ4E9ZELwv_52GQw~~&x5=0&f=json HTTP/1.1'
"""


def get_link(url):
    global num
    response = requests.get(url, headers=headers, proxies=proxy.get_proxy(proxies)[-1], verify=False)
    if response.status_code != 200:
        return False
    html = response.text
    print(html)
    datas = re.sub(r'amp;', '', html)
    datas = re.sub(r'\\', '', datas)
    # print(datas)
    titles = re.findall(r'"title"\:(.*?),"digest"', datas)
    urls = re.findall(r'"content_url":(.*?),"source_url"', datas)
    if not (titles or urls):
        return False
    for title, url in zip(titles, urls):
        print(title)
        print(url)
        print('-' * 100)
    num += len(urls)
    time.sleep(random.uniform(5, 10))


def get_read_like():
    headers_ = """Host: mp.weixin.qq.com
Accept: */*
X-Requested-With: XMLHttpRequest
Accept-Language: zh-cn
Accept-Encoding: br, gzip, deflate
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
Origin: https://mp.weixin.qq.com
User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 12_0_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16A404 MicroMessenger/6.7.3(0x16070321) NetType/WIFI Language/zh_CN
Connection: keep-alive
Referer: https://mp.weixin.qq.com/s?__biz=MjM5NTcxODg0MA==&mid=2689803578&idx=2&sn=7475c7881e820749c878f9031301fcdf&chksm=8353b6edb4243ffbbefcc10a055fae49cc2f317138c85b30236d1205742e9d6087b56a35e09d&scene=4&ascene=0&devicetype=iOS12.0.1&version=16070322&nettype=WIFI&abtest_cookie=BgABAAgACgALAA0AEwAUAAYAnYYeACWXHgBZmR4AhZkeAIiZHgCNmR4AAAA%3D&lang=zh_CN&fontScale=100&pass_ticket=fRfhx%2BOVXGtK6E4eRbW9q%2BcqS%2FoIhmoXVW8jO%2BoY%2F%2B0%3D&wx_header=1
Content-Length: 868
Cookie: devicetype=iOS12.0.1; lang=zh_CN; pass_ticket=fRfhx+OVXGtK6E4eRbW9q+cqS/oIhmoXVW8jO+oY/+0=; rewardsn=; version=16070322; wap_sid2=CKvk+TYSXEVxQnNVOExZTnk5QWtpaWNkX3JIaHQ1QlRDR3V6eW9hY09nWXBCaVpBdmFQQ25mbktmQTJlVVA4cnZyTTFyYlk4c0JtUHVNbW83VG1TRk9ZSnF0N1R0VURBQUF+MLDe9d4FOA1AAQ==; wxtokenkey=777; wxuin=115241515; pgv_pvid=4600968294; RK=RCRBnFF1YT; pt2gguin=o0527439841; ptcz=6481a5818b1db6aff56ee2f0524dcc6716c68dd2ceb914c16c720fc3f8bac89f; sd_cookie_crttime=1522933505177; sd_userid=7641522933505177; r=0.9960219786394555&__biz=MjM5NTcxODg0MA%3D%3D&appmsg_type=9&mid=2689803578&sn=7475c7881e820749c878f9031301fcdf&idx=2&scene=4&title=%25E5%25AD%25A6Excel%25E5%2587%25BD%25E6%2595%25B0%25E5%2585%25AC%25E5%25BC%258F%25EF%25BC%258C%25E6%2580%258E%25E8%2583%25BD%25E4%25B8%258D%25E4%25BC%259A%25E8%25BF%2599%25E4%25B8%25AA%25E7%25BB%2584%25E5%2590%2588%25E5%25A5%2597%25E8%25B7%25AF%25EF%25BC%259F&ct=1540511100&abtest_cookie=BgABAAgACgALAA0AEwAUAAYAnYYeACWXHgBZmR4AhZkeAIiZHgCNmR4AAAA%3D&devicetype=iOS12.0.1&version=16070322&is_need_ticket=0&is_need_ad=1&comment_id=518065699936370688&is_need_reward=0&both_ad=0&reward_uin_count=0&send_time=&msg_daily_idx=1&is_original=0&is_only_read=1&req_id=03175IK3sdgA4GK52gvV5W8d&pass_ticket=fRfhx%25252BOVXGtK6E4eRbW9q%25252BcqS%25252FoIhmoXVW8jO%25252BoY%25252F%25252B0%25253D&is_temp_url=0&item_show_type=undefined&tmp_version=1"""
    headers = {each.split(':', 1)[0]: each.split(':', 1)[1].replace(' ', '', 1) for each in headers_.split('\n')}
    print(headers)
    data = {
        'f': 'json',
        'mock': '',
        'uin': '777',
        'key': '777',
        'pass_ticket': 'fRfhx%252BOVXGtK6E4eRbW9q%252BcqS%252FoIhmoXVW8jO%252BoY%252F%252B0%253D',
        'wxtoken': '777',
        'devicetype': 'iOS12.0.1',
        'clientversion': '16070322',
        'appmsg_token': '981_EBYfFC6HJhwtVKviIxa4Ha5HIpDSWmPJRi3mRmmk1CZD5zN9l0x9gHJiMlA~',
        'x5': '0'
    }
    url = 'https://mp.weixin.qq.com/mp/getappmsgext'
    s = requests.session()
    res = requests.post(url, data=data, headers=headers, verify=False)
    html = res.text
    print(html)


def main():
    page_num = 0
    # while True:
    for i in range(0, page_end):
        url = start_url.format(page_num * 10)
        headers['referer'] = url
        if get_link(url):
            break
        else:
            get_link(url)
            page_num += 1

    print('共抓取{}篇文章'.format(num))


if __name__ == '__main__':
    main()
    # get_read_like()
