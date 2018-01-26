import requests, xlrd, time, json

# 帐号密码信息读取
def getUserInfo():
    try:
        data = xlrd.open_workbook('data.xlsx')    # 读取工作簿数据 该工作簿存放帐号和密码信息 data.xlsx目前只存一组信息
        table = data.sheets()[0]    # 读取工作簿中的工作表数据 默认为第一个工作表 下标为0
        
        nrows = table.nrows    # 保存工作表的有效行数
        ncols = table.ncols    # 保存工作表的有效列数
        
        # 读取xlsx文件的时候 python自动识别数字并转换为浮点数 但我们实际需要的是文本 这里需要进行操作
        account = str((int)(table.cell(0,0).value))    # 去除浮点 转换为文本 即字符串 
        password = table.cell(0,1).value    # 这里python会自动识别成文本进行保存 因此不需要处理

        user_data = {
            'account': account,
            'password': password,
            'captcha': None
        }

        print('读取用户数据成功')
    except:
        print('读取用户数据失败')

    return user_data

def login(user_data):
    '''
    登录
    '''
    session = requests.session()    # session对象提供Cookie的持久化和连接池功能
    login_url = 'https://www.yiban.cn/login/doLoginAjax'
    login_response = session.post(login_url, user_data)
    try:
        if json.loads(login_response.text)['message'] == '操作成功':
            print('Login Sucessful 登录成功')
    except:
        print('Login Failed 登录失败')
    return session

def send_feed(session):
    '''
    动态发布
    '''
    feed_data = {
        'content': 'Hello World!',
        'privacy': '0',
        'dom': '.js-submit'
    }

    send_feed_url = 'http://www.yiban.cn/feed/add'
    send_feed_response = session.post(send_feed_url, feed_data)

    try:
        if json.loads(send_feed_response.text)['message'] == '操作成功':
            print('动态发布成功')
    except:
        print('动态发布失败')

if __name__ == '__main__':
    user_data = getUserInfo()    # 获得用户信息
    session = login(user_data)    # 登录响应
    send_feed(session)    # 发布动态