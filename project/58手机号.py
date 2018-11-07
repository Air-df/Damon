from selenium import webdriver
from bs4 import BeautifulSoup
from plugins import proxy
import time



proxies = proxy.get_proxies()
url = 'https://bj.58.com/ershouche/36031247924997x.shtml?typos=topinfo_l1&infotype=z_2_576574&merABTest=WBERSHOUCHE_160_659842083&merShow=true&iuType=z_2&PGTID=0d30001d-0000-1e2e-ed7b-98dfcffc8e70&ClickID=26&adtype=3'
service_args = [
                '--proxy={}'.format(proxy.get_proxy(proxies)[-1]),  # 代理http://IP:PORT 只设置该项也可以
                '--load-images=no',  # 图片加载开关
                '--disk-cache=yes',  # 缓存控制
                '--ignore-ssl-errors=true',  # 忽略ssl错误
            ]
driver = webdriver.PhantomJS(service_args=service_args)
driver.get(url)
time.sleep(2)
driver.find_element_by_css_selector('div.gettell > span.tel-txt').click()
time.sleep(1)
html = driver.page_source
soup = BeautifulSoup(html, 'lxml')
item = soup.select('div.phone_num.clearfix')[0].text
print(item)
