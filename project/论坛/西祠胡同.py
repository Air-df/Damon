import re
import time
import json
import random
import traceback
import requests

from bs4 import BeautifulSoup
from faker import Factory
from plugins import proxy

headers = {
    'User-Agent': Factory().create().user_agent(),
    'Referer': 'https://www.baidu.com'
}
proxies = proxy.get_proxies()
url = 'https://tieba.baidu.com/p/3743321735?pn=1'


def get_comments(url):
    res = requests.get(url, headers=headers, proxies=proxy.get_proxy(proxies)[-1], verify=False)
    html = res.text
    soup = BeautifulSoup(html, 'lxml')


get_comments(url)