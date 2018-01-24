import requests, xlrd, time, os
from http import cookiejar

# 头部Header信息伪造
headers = {
    'Host': 'www.yiban.cn',
    'Refer': 'http://www.yiban.cn/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
}

# 使用Cookie进行登录
session = requests.session()    # session对象提供Cookie的持久化和连接池功能
session.cookies = cookiejar.LWPCookieJar(filename='cookies.txt')
try:
    print(session.cookies)
    session.cookies.load(ignore_discard=True)
except:
    print('Load Cookies Failed 暂无Cookie信息')

# 帐号密码信息读取
data = xlrd.open_workbook('data.xlsx')    # 读取工作簿数据 该工作簿存放帐号和密码信息 data.xlsx目前只存一组信息
table = data.sheets()[0]    # 读取工作簿中的工作表数据 默认为第一个工作表 下标为0
nrows = table.nrows    # 保存工作表的有效行数
ncols = table.ncols    # 保存工作表的有效列数
# 读取xlsx文件的时候 python自动识别数字并转换为浮点数 但我们实际需要的是文本 这里需要进行操作
account = str((int)(table.cell(0,0).value))    # 去除浮点 转换为文本 即字符串 
password = table.cell(0,1).value    # 这里python会自动识别成文本进行保存 因此不需要处理

def getCaptcha():
    '''
    获取验证码信息
    第一阶段 使用人工识别方法
    第二阶段 pytesser自动识别
    '''
    t = str(int(time.time()))
    captcha_url = 'https://www.yiban.cn/captcha/index?' + t
    print(captcha_url)
    r = session.get(captcha_url, headers=headers)
    with open('captcha.png', 'wb') as f:
        f.write(r.content)
    # 这部分有问题 图片似乎没有保存下来 只有0字节
    captcha = input('验证码: ')
    return captcha

def login(account, password):
    '''
    登录
    '''
    login_url = 'https://www.yiban.cn/login/doLoginAjax'
    form_data = {
        'account': account,
        'password': password,
        'captcha': getCaptcha()
    }
    response = session.post(login_url, data=form_data, headers=headers)
    login_code = response.json()
    print(login_code['message'])
    for i in session.cookies:
        print(i)
    session.cookies.save()

def isLogin():
    '''
    判断是否已经登录 目前用不到这个功能 先放着
    第一阶段 单个帐号判断与匹配
    第二阶段 多账号判断匹配 比较简单 只要看状态码code是否是200即可
    '''
    pass

if __name__ == '__main__':
    login(account, password)