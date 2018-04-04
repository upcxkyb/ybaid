import requests, xlrd, time, json, re, configparser, random
from bs4 import BeautifulSoup
from urllib.parse import urlparse

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
}

# 时间获取
def get_time():
    return time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))

# 帐号密码信息读取
def getUserInfo():
    try:
        config = configparser.ConfigParser()
        config.read('info.ini')
        
        user_data = {
            'account': config['Information']['account'],
            'password': config['Information']['password'],
            'captcha': None
        }

        print('读取用户数据成功')
        return user_data
    except:
        print('读取用户数据失败')
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
    user_data = getUserInfo()    # 获得用户信息
    session = login(user_data)    # 登录响应
    crowed_html = get_html()    # 爬取相应页面内容

    # send_feed(session)    # 发布动态
    basic_egpa(session, crowed_html)
    build_gpa(session, crowed_html)
    
    # 点赞模块
    article_ids = getArticleIds(session)
    for article_id in article_ids:
        up_article(session, article_id)
    
    print('完成时间 ' + get_time())
    