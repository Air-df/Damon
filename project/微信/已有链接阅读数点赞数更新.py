from appium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import pymongo

PLATFORM = 'Android'
deviceName = 'gemini'
app_package = 'com.tencent.mm'
app_activity = '.ui.LauncherUI'
driver_server = 'http://127.0.0.1:4723/wd/hub'


class Moments():
    def __init__(self):
        self.desired_caps = {
            'platformName': PLATFORM,
            'deviceName': deviceName,
            'appPackage': app_package,
            'appActivity': app_activity,
            'noreset': True
        }
        self.driver = webdriver.Remote(driver_server, self.desired_caps)
        self.wait = WebDriverWait(self.driver, 3000)
        # self.client = pymongo.MongoClient()
        # self.db = self.client.weixin
        # self.collection = self.db.weixin

    def login(self):
        time.sleep(15)
        print('点击登陆按钮——————')
        login = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'android.widget.ImageView')))
        login.click()
        print('登陆按钮点击结束——————')
        # 输入手机号
        phone = self.wait.until(EC.presence_of_element_located((By.ID, 'com.tencent.mm:id/ji')))
        phone_num = input('请输入手机号：')
        phone.send_keys(phone_num)
        print('点击下一步中')
        button = self.wait.until(EC.presence_of_element_located((By.ID, 'com.tencent.mm:id/ast')))
        button.click()
        pass_w = input('请输入密码：')
        password = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'Inspector__highlighter-box___Oi319 Inspector__inspected-element-box___3mBB4')))
        password.send_keys(pass_w)

        login = self.driver.find_element_by_id('com.tencent.mm:id/ast')
        login.click()
        # 提示 叉掉
        tip = self.wait.until(EC.element_to_be_clickable((By.ID, 'com.tencent.mm:id/au9')))
        tip.click()

    def enter(self):
        print('点击发现——')
        tab = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//android.widget.FrameLayout[@content-desc="当前所在页面,与的聊天"]/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.view.View/android.widget.FrameLayout[1]/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.RelativeLayout/android.widget.LinearLayout/android.widget.RelativeLayout[3]/android.widget.LinearLayout/android.widget.RelativeLayout/android.widget.ImageView[1]')))
        print('已经找到发现按钮')
        time.sleep(6)
        tab.click()
        self.wait.until(EC.text_to_be_present_in_element((By.ID, 'com.tencent.mm:id/cdj'), '发现'))
        print('点击朋友圈')
        friends = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, '//*[@resource-id="android:id/list"]/*[@class="android.widget.LinearLayout"][1]')))
        friends.click()

    def crawl(self):
        while True:
            items = self.wait.until(EC.presence_of_all_elements_located(
                (By.XPATH, '//*[@resource-id="com.tencent.mm:id/dja"]//*[@class="android.widget.FrameLayout"]')))
            self.driver.swipe(300, 1000, 300, 300)
            for item in items:
                try:
                    nickname = item.find_element_by_id('com.tencent.mm:id/as6').get_attribute('text')
                    print(nickname)
                    content = item.find_element_by_id('com.tencent.mm:id/dkf').get_attribute('text')
                    print(content)
                    data = {'nickname': nickname,
                            'content': content}
                    # self.collection.update({'nickname': nickname, 'content': content}, {'$set': data}, True)

                except:
                    pass

    def main(self):
        self.login()
        self.enter()
        self.crawl()


M = Moments()
M.main()
