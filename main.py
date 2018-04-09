import requests, xlrd, time, json, re, configparser, random, os
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from base64 import b64encode
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from aip import AipOcr
from PIL import Image

######################################## 登录相关模块 ########################################
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}


# 时间获取
def get_time():
    return time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
def get_time2():
    return time.strftime('%Y-%m-%d-%H-%M', time.localtime(time.time()))

'''
模拟 JSEncrypt 加密
加密方式为 PKCS1_v1_5
'''


def rsaEncrypt(password, key):
    cipher = PKCS1_v1_5.new(RSA.importKey(key))
    return b64encode(cipher.encrypt(password.encode()))


# 获取验证码的URL,和时间有关
def getCaptchaURL():
    format_time = time.strftime("%a %b %d %Y %H:%M:%S", time.localtime())
    time_list = format_time.split(' ')
    time_string = '%20'.join(time_list)
    captcha_url = 'https://www.yiban.cn/captcha/index?' + time_string + '%20GMT+0800%20(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)'
    return captcha_url


# 帐号密码信息读取,密码采用加密方式传输
def getUserInfo(captcha, keytime, key):
    try:
        config = configparser.ConfigParser()
        config.read('info.ini')
        raw_psw = config['Information']['password']
        Psw = rsaEncrypt(raw_psw, key)
        user_data = {
            'account': config['Information']['account'],
            'password': Psw,
            'captcha': captcha,
            'keysTime': keytime
        }

        print('读取用户数据成功')
        return user_data
    except:
        print('读取用户数据失败')


######################################## 验证码本地处理模块 ########################################

# 二值化图片，threshold为阈值
def get_bin_table(threshold=110):
    """
    获取灰度转二值的映射table
    :param threshold:
    :return:
    """
    table = []
    for i in range(256):
        if i < threshold:
            table.append(0)
        else:
            table.append(1)

    return table


# 九宫格降噪法
def sum_9_region(img, x, y):
    """
    9邻域框,以当前点为中心的田字框,黑点个数
    :param x:
    :param y:
    :return:
    """
    # todo 判断图片的长宽度下限
    cur_pixel = img.getpixel((x, y))  # 当前像素点的值
    width = img.width
    height = img.height

    if cur_pixel == 1:  # 如果当前点为白色区域,则不统计邻域值
        return 0

    if y == 0:  # 第一行
        if x == 0:  # 左上顶点,4邻域
            # 中心点旁边3个点
            sum = cur_pixel \
                  + img.getpixel((x, y + 1)) \
                  + img.getpixel((x + 1, y)) \
                  + img.getpixel((x + 1, y + 1))
            return 4 - sum
        elif x == width - 1:  # 右上顶点
            sum = cur_pixel \
                  + img.getpixel((x, y + 1)) \
                  + img.getpixel((x - 1, y)) \
                  + img.getpixel((x - 1, y + 1))

            return 4 - sum
        else:  # 最上非顶点,6邻域
            sum = img.getpixel((x - 1, y)) \
                  + img.getpixel((x - 1, y + 1)) \
                  + cur_pixel \
                  + img.getpixel((x, y + 1)) \
                  + img.getpixel((x + 1, y)) \
                  + img.getpixel((x + 1, y + 1))
            return 6 - sum
    elif y == height - 1:  # 最下面一行
        if x == 0:  # 左下顶点
            # 中心点旁边3个点
            sum = cur_pixel \
                  + img.getpixel((x + 1, y)) \
                  + img.getpixel((x + 1, y - 1)) \
                  + img.getpixel((x, y - 1))
            return 4 - sum
        elif x == width - 1:  # 右下顶点
            sum = cur_pixel \
                  + img.getpixel((x, y - 1)) \
                  + img.getpixel((x - 1, y)) \
                  + img.getpixel((x - 1, y - 1))

            return 4 - sum
        else:  # 最下非顶点,6邻域
            sum = cur_pixel \
                  + img.getpixel((x - 1, y)) \
                  + img.getpixel((x + 1, y)) \
                  + img.getpixel((x, y - 1)) \
                  + img.getpixel((x - 1, y - 1)) \
                  + img.getpixel((x + 1, y - 1))
            return 6 - sum
    else:  # y不在边界
        if x == 0:  # 左边非顶点
            sum = img.getpixel((x, y - 1)) \
                  + cur_pixel \
                  + img.getpixel((x, y + 1)) \
                  + img.getpixel((x + 1, y - 1)) \
                  + img.getpixel((x + 1, y)) \
                  + img.getpixel((x + 1, y + 1))

            return 6 - sum
        elif x == width - 1:  # 右边非顶点
            # print('%s,%s' % (x, y))
            sum = img.getpixel((x, y - 1)) \
                  + cur_pixel \
                  + img.getpixel((x, y + 1)) \
                  + img.getpixel((x - 1, y - 1)) \
                  + img.getpixel((x - 1, y)) \
                  + img.getpixel((x - 1, y + 1))

            return 6 - sum
        else:  # 具备9领域条件的
            sum = img.getpixel((x - 1, y - 1)) \
                  + img.getpixel((x - 1, y)) \
                  + img.getpixel((x - 1, y + 1)) \
                  + img.getpixel((x, y - 1)) \
                  + cur_pixel \
                  + img.getpixel((x, y + 1)) \
                  + img.getpixel((x + 1, y - 1)) \
                  + img.getpixel((x + 1, y)) \
                  + img.getpixel((x + 1, y + 1))
            return 9 - sum


def remove_noise_pixel(img, noise_point_list):
    """
    根据噪点的位置信息，消除二值图片的黑点噪声
    :type img:Image
    :param img:
    :param noise_point_list:
    :return:
    """
    for item in noise_point_list:
        img.putpixel((item[0], item[1]), 1)


# 图片降噪核心算法
def captchaDenoise():
    image = Image.open('rawcap.png')
    imgry = image.convert('L')  # 转化为灰度图
    table = get_bin_table()
    img_gray = imgry.point(table, '1')
    print('验证码降噪-二值化完成')
    # 九宫格去噪点操作
    width = img_gray.width
    height = img_gray.height
    noise_point_list = []
    for i in range(0, width):
        for j in range(0, height):
            num = sum_9_region(img_gray, i, j)
            if (0 < num < 4) and img_gray.getpixel((i, j)) == 0:  # 找到孤立点
                pos = (i, j)  #
                noise_point_list.append(pos)
    remove_noise_pixel(img_gray, noise_point_list)
    print('去除噪点完成')
    filename = get_time2() + '.png'
    img_gray.save(filename)
    print('新验证码保存本地完成')
    return filename


######################################## 百度API识别验证码模块 ########################################
def captcha_recon(filename):
    APP_ID = '11058605'
    API_KEY = 'aGc6HEbsdeF7xmRYfp3t8mES'
    SECRET_KEY = 'hggXcZ7HCnEEdt5KMtnB1YPGEVElMIwL'
    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
    with open(filename, 'rb') as fp:
        image = fp.read()
    options = {
        'detect_direction': 'true',
        'language_type': 'CHN_ENG',
    }
    response = client.basicGeneral(image, options)
    try:
        return response['words_result'][0]['words']
    except:
        return ''


'''
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
'''


def login():
    '''
    登录
    '''
    base_url = 'https://www.yiban.cn/login'
    login_url = 'https://www.yiban.cn/login/doLoginAjax'
    session = requests.session()  # session对象提供Cookie的持久化和连接池功能
    # 模拟登录到网页
    LoginPage = session.get(base_url, headers=headers, timeout=10)
    # 查找静态页面中加密方式，验证方式
    print('模拟登录成功')
    RsaKey = re.search(r'data-keys=\'([\s\S]*?)\'', LoginPage.text).group(1)
    KeysTime = re.search(r'data-keys-time=\'(.*?)\'', LoginPage.text).group(1)
    # 无验证码登录测试
    user_data = getUserInfo(None, KeysTime, RsaKey)  # 获得用户信息
    login_response = session.post(login_url, headers=headers, data=user_data, timeout=10)
    if json.loads(login_response.text)['message'] == '操作成功':
        print('Login Sucessful 登录成功')
    else:
        print('Login Failed 无验证码状态登录失败，正在尝试使用验证码自动化登录')
        while 1:
            captchaURL = getCaptchaURL()
            cap_img = session.get(captchaURL)
            with open("rawcap.png", 'wb') as fp:
                fp.write(cap_img.content)
            file_name = captchaDenoise()
            cap_text = captcha_recon(file_name)
            if cap_text == '':
                continue
            print('验证码是： '+cap_text)
            os.remove(file_name)
            time.sleep(1)
            data_c = getUserInfo(cap_text, KeysTime, RsaKey)
            login_response = session.post(login_url, headers=headers, data=data_c, timeout=10)
            if json.loads(login_response.text)['message'] == '操作成功':
                print('Login Sucessful 含验证码登录成功')
                break
    return session

def login_mp(session):
    '''
    session = requests.session()
    login_mp_url = 'https://mp.yiban.cn/login/loginAjax'
    login_mp_response = session.post(login_mp_url, data=user_data, headers=headers)
    
    data = {'uid': '537058'}    # 机构群超级管理员登录
    login_mp_choice_url = 'https://mp.yiban.cn/login/choiceAjax'
    login_mp_choice_response = session.post(login_mp_choice_url, data=data, headers=headers)
    '''

    uu = 'http://mp.yiban.cn/backend/tasks'

    data = {'id': '5572667'}
    mp_index_url = 'http://www.yiban.cn/manage/Gforum/push?'
    query_params = {
        'id': '37508180',    # 变化，找不到id
        'position': '2',
        'channel_id': '70922',
        'group_id': '218963',
        'article_id': '36677502'    # 变化
    }
    url = 'http://www.yiban.cn/Manage/Gforum/index/group_id/218963/user_id/5370538?'
    pa = {'is_notice': '2'}
    html = session.get(mp_index_url, params=pa, headers=headers)
    print(html)

    # 本代码无用



def get_id():
    pass

def get_html():
    crow_url = 'http://www.upc.edu.cn/'
    try:
        r = requests.get(crow_url, headers=headers)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        print('爬取失败')
    
def get_topic_title(num, html):
    '''
    获取置顶全国头条标题
    '''
    soup = BeautifulSoup(html, 'html.parser')
    figcaptions = soup.find_all('figcaption', 'pull-left')
    univs = []
    titles = []
    for figcaption in figcaptions:
        a = figcaption.find('a')
        span = a.find('span')
        if span == None:
            continue
        univs.append(span.b.string)
        title_str = re.search(r'</b>(.*?)</span>', str(span))[0]    # 正则匹配
        tstr = re.sub(r'<[^>]+>', '', title_str)    # 去除HTML标签
        titles.append(tstr)

    return '【他山之石】' + univs[num] + '-' + titles[num]

def get_topic_content(num, html):
    '''
    获取置顶全国头条内容
    '''
    soup = BeautifulSoup(html, 'html.parser')
    figcaptions = soup.find_all('figcaption', 'pull-left')
    hrefs = []
    contents = []
    for figcaption in figcaptions:
        a = figcaption.find('a')
        p = figcaption.find('p')
        if a == None:
            continue
        if p == None:
            continue
        hrefs.append(str(a['href']))
        tstr = re.sub(r'<[^>]+>', '', str(p))
        contents.append(tstr)
    
    return '<p><a href="' + hrefs[num] + '" targets="_blank">' + contents[num] + '</a></p>'

def get_news_odd_title(num, html):
    '''
    获取新闻头条奇数列表的标题
    '''
    soup = BeautifulSoup(html, 'html.parser')
    odd_lis = soup.find_all('li', 'news-item odd')
    univs = []
    titles = []
    for odd_li in odd_lis:
        a = odd_li.find('a')
        span = a.find('span')
        if span == None:
            continue
        univs.append(span.b.string)
        title_str = re.search(r'</b>(.*?)</span>', str(span))[0]    # 正则匹配
        tstr = re.sub(r'<[^>]+>', '', title_str)    # 去除HTML标签
        titles.append(tstr)
    
    return '【他山之石】' + univs[num] + '-' + titles[num]

def get_news_odd_content(num, html):
    '''
    获取新闻头条奇数列表的内容
    '''
    soup = BeautifulSoup(html, 'html.parser')
    odd_lis = soup.find_all('li', 'news-item odd')
    univs = []
    hrefs = []
    titles = []
    for odd_li in odd_lis:
        a = odd_li.find('a')
        hrefs.append(str(a['href']))
        span = a.find('span')
        if span == None:
            continue
        univs.append(span.b.string)
        title_str = re.search(r'</b>(.*?)</span>', str(span))[0]    # 正则匹配
        tstr = re.sub(r'<[^>]+>', '', title_str)    # 去除HTML标签
        titles.append(tstr)

    return '<p style="text-align: center;"><a href="' + hrefs[num] + '" target="_blank" title="' + '【转】' + univs[num] + '-' + titles[num] + '" style="text-decoration: underline; font-size: 16px; font-family: 宋体, SimSun; color: rgb(0, 0, 0);"><span style="font-size: 16px; font-family: 宋体, SimSun; color: rgb(0, 0, 0);">' + '【转】' + univs[num] + '-' + titles[num] + '</span></a><br/></p>'

def get_upc_news_title(html, num):
    '''
    获取学校主页石大要闻标题
    '''
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', 'news_con')
    aes = div.find_all('a')
    titles = []
    for a in aes:
        titles.append(a['title'])
    
    return '【石大要闻】' + titles[num]

def get_upc_news_content(html, num):
    '''
    构造内容
    '''
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', 'news_con')
    aes = div.find_all('a')
    titles = []
    hrefs = []
    for a in aes:
        titles.append(a['title'])
        hrefs.append(a['href'])
    
    return '<p style="text-align: center;"><a href="' + hrefs[num] + '" target="_blank" title="' + '【石大要闻】' + titles[num] + '" style="text-decoration: underline; font-size: 16px; font-family: 宋体, SimSun; color: rgb(0, 0, 0);"><span style="font-size: 16px; font-family: 宋体, SimSun; color: rgb(0, 0, 0);">' + '【石大要闻】' + titles[num] + '</span></a><br/></p>'

def get_upcaca_title(html, num):
    '''
    获取学校主页标题
    '''
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', 'aca_news_con')
    aes = div.find_all('a')
    titles = []
    for a in aes:
        titles.append(a['title'])
    
    return '【学术石大】' + titles[num]

def get_upcaca_content(html, num):
    '''
    构造内容
    '''
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', 'aca_news_con')
    aes = div.find_all('a')
    titles = []
    hrefs = []
    for a in aes:
        titles.append(a['title'])
        hrefs.append(a['href'])
    
    return '<p style="text-align: center;"><a href="' + hrefs[num] + '" target="_blank" title="' + '【学术石大】' + titles[num] + '" style="text-decoration: underline; font-size: 16px; font-family: 宋体, SimSun; color: rgb(0, 0, 0);"><span style="font-size: 16px; font-family: 宋体, SimSun; color: rgb(0, 0, 0);">' + '【学术石大】' + titles[num] + '</span></a><br/></p>'

def send_feed(session):
    '''
    发布动态
    '''
    feed_data = {
        'content': get_time(),
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

def send_class_topic(session, title, content):
    '''
    发布班级群话题
    '''
    data = {
        'puid': '5572667',    # 学院机构群id
        'pubArea': '232753,232751,232749,232755,232759,232757,232761,232777,232779,232781,233325,223295,223311,223331,223391,223397,223399,223393,223333,223313,223305,223309,223327,223363,223395,223401,223403,228957,228953,228959,232763,232767,229425,228955,232769,232775,234391,234397,234399,234393,232771,232773,234389,234401,234395,330093,303274,234419,234413,234407,234405,234411,234417,303272,330091,303270,234415,234409,234403,330103,330097,330099,330095,330101,334923,334929,334935,334937,334931,334925,330087,334927,334933,411813,411815,414633,414641,414647,414653,414659,414661,414655,414649,414643,414637,414639,414645,414651,414657,414663,429159,429161,429163,429165,429167,429169',    # 班级id 多个班级用列表
        'title': title,
        'content': content,
        'isNotice': 'false',
        'dom': '.js-submit'
    }

    send_topic_url = 'http://www.yiban.cn/forum/article/addAjax'
    send_topic_response = session.post(send_topic_url, data)

    try:
        if json.loads(send_topic_response.text)['message'] == '操作成功':
            print('班级群话题发布成功')
    except:
        print('班级群话题发布失败')

def send_class_vote(session):
    '''
    发布班级群投票
    '''
    data = {
        'puid': '5572667',    # 学院机构群
        'scope_ids': '232753,232751,232749,232755,232759,232757,232761,232777,232779,232781,233325,223295,223311,223331,223391,223397,223399,223393,223333,223313,223305,223309,223327,223363,223395,223401,223403,228957,228953,228959,232763,232767,229425,228955,232769,232775,234391,234397,234399,234393,232771,232773,234389,234401,234395,330093,303274,234419,234413,234407,234405,234411,234417,303272,330091,303270,234415,234409,234403,330103,330097,330099,330095,330101,334923,334929,334935,334937,334931,334925,330087,334927,334933,411813,411815,414633,414641,414647,414653,414659,414661,414655,414649,414643,414637,414639,414645,414651,414657,414663,429159,429161,429163,429165,429167,429169',    # 班级
        'title': get_time(),    # 投票标题
        'subjectTxt': get_time() + ' 你做了什么？',    # 投票说明
        'subjectPic': '',    # 投票图片 默认为无
        'options_num': '3',    # 投票选项数量
        'scopeMin': '1',
        'scopeMax': '1',
        'minimum': '1',
        'voteValue': '2019-12-27 14:00',    # 投票结束时间
        'voteKey': '2',
        'public_type': '1',
        'isAnonymous': '2',    # 是否匿名投票 1为不匿名 2为匿名
        'votelsCaptcha': '0',    # 投票时是否开启验证码 0为关闭
        'istop': '1',    # 是否置顶 1为不置顶 2为置顶
        'sysnotice': '2',
        'isshare': '1',
        'rsa': '1',
        'dom': '.js-submit',
        # 'group_id': '223395',
        'subjectTxt_1': '学习',    # 投票选项1文本内容
        'subjectTxt_2': '学习',    # 投票选项2文本内容
        'subjectTxt_3': '学习'    # 投票选项3文本内容
    }

    send_vote_url = 'http://www.yiban.cn/vote/vote/add'
    send_vote_response = session.post(send_vote_url, data=data)

    try:
        if json.loads(send_vote_response.text)['message'] == '操作成功':
            print('班级群投票发布成功')
    except:
        print('班级群投票发布失败')

def send_institute_topic(session, title, content):
    '''
    发布机构群话题
    '''
    data = {
        'puid': '5370538',
        'pubArea': '218963',
        'title': title,
        'content': content,
        'Sections_id': '0',
        'isNotice': 'false',
        'dom': '.js-submit'
    }

    send_topic_url = 'http://www.yiban.cn/forum/article/addAjax'
    send_topic_response = session.post(send_topic_url, data)

    try:
        if json.loads(send_topic_response.text)['message'] == '操作成功':
            print('机构群话题发布成功')
    except:
        print('机构群话题发布失败')

def send_institute_vote(session):
    pass


def basic_egpa(session, html):
    upc_news_title_1 = get_upc_news_title(html, 0)
    upc_news_content_1 = get_upc_news_content(html, 0)
    upc_aca_title_1 = get_upcaca_title(html, 0)
    upc_aca_content_1 = get_upcaca_content(html, 0)
    upc_news_title_2 = get_upc_news_title(html, 1)
    upc_news_content_2 = get_upc_news_content(html, 1)
    upc_aca_title_2 = get_upcaca_title(html, 1)
    upc_aca_content_2 = get_upcaca_content(html, 1)

    send_class_topic(session, upc_news_title_1, upc_news_content_1)    # 发布新闻话题1
    send_class_topic(session, upc_aca_title_1, upc_aca_content_1)    # 发布学术话题1
    send_class_vote(session)    # 发布投票
    send_class_topic(session, upc_news_title_2, upc_news_content_2)    # 发布新闻话题2
    send_class_topic(session, upc_aca_title_2, upc_aca_content_2)    # 发布学术话题2
    send_class_vote(session)    # 发布投票

def build_gpa(session, html):
    upc_news_title_1 = get_upc_news_title(html, 0)
    upc_news_content_1 = get_upc_news_content(html, 0)
    upc_aca_title_1 = get_upcaca_title(html, 0)
    upc_aca_content_1 = get_upcaca_content(html, 0)
    upc_news_title_2 = get_upc_news_title(html, 1)
    upc_news_content_2 = get_upc_news_content(html, 1)
    upc_aca_title_2 = get_upcaca_title(html, 1)
    upc_aca_content_2 = get_upcaca_content(html, 1)

    send_institute_topic(session, upc_news_title_1, upc_news_content_1)    # 发布机构群新闻话题1
    send_institute_topic(session, upc_aca_title_1, upc_aca_content_1)    # 发布机构群学术话题1
    # send_institute_vote(session)    # 发布机构群投票
    send_institute_topic(session, upc_news_title_2, upc_news_content_2)    # 发布机构群新闻话题2
    send_institute_topic(session, upc_aca_title_2, upc_aca_content_2)    # 发布机构群学术话题2
    # send_institute_vote(session)    # 发布机构群投票



def page_view(num):
    '''
    浏览量
    '''
    data = {
       'channel_id': '70922',
       'puid': '5370538',
       'article_id': '28292666',
       'origin': '0'
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
    }

    send_topic_url = 'http://www.yiban.cn/forum/article/showAjax'
    send_topic_response = requests.post(send_topic_url, headers=headers, data=data)

    try:
        if json.loads(send_topic_response.text)['message'] == '操作成功':
            print('成功 ' + str(num))
    except:
        print('失败 ' + str(num))

def getArticleIds(session):
    institute_url = 'http://www.yiban.cn/Newgroup/indexOrg/group_id/218963/puid/5370538'
    institute_html = session.get(institute_url, headers=headers).text

    institute_soup = BeautifulSoup(institute_html, 'html.parser')
    divs = institute_soup.find_all('div', 'lfi_title')
    article_ids = []
    for div in divs:
        article_url = div.find('a')['href']
        article_id = re.findall('\d+', str(article_url))[3]    # 选择arricle_id
        article_ids.append(article_id)

    return article_ids

def up_article(session, article_id):
    up_url = 'http://www.yiban.cn/forum/article/upArticleAjax'
    up_data = {
        'article_id': article_id,
        'channel_id': '70922',    # 不变
        'puid': '5370538'    # 不变
    }
    session.post(up_url, data=up_data, headers=headers)

if __name__ == '__main__':
    session = login()    # 登录响应
    crowed_html = get_html()    # 爬取相应页面内容

    # send_feed(session)    # 发布动态
    basic_egpa(session, crowed_html)
    build_gpa(session, crowed_html)
    
    # 点赞模块
    article_ids = getArticleIds(session)
    for article_id in article_ids:
        up_article(session, article_id)
    
    print('完成时间 ' + get_time())
