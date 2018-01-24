import requests
import xlrd
from http import cookiejar

# 头部Header信息伪造
headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
}

# 使用Cookie进行登录
session = requests.session()    # session对象提供Cookie的持久化和连接池功能
session.cookies = cookiejar.LWPCookieJar(filename='cookies.txt')
try:
    session.cookies.load(ignore_discard=True)
except LoadError:
    print('Load Cookies Failed 暂无Cookie信息')

# 获取验证码信息
def getCaptcha():
    pass

# 账号信息读取
def getAccount():
    pass
    # 使用python的xlrd官方库 已实现 待整合

# 登录
def login(account, password):
    login_url = 'https://www.yiban.cn/login/doLoginAjax'
    form_data = {
        'account': account,
        'password': password,
        'captcha': getCaptcha()
    }

if __name__ == '__main__':
    getAccount()    # 获取帐号信息 填入account与password
    account = ''
    password = ''
    login(account, password)