# -*- coding: utf-8 -*-
__author__ = 'Dee'
__date__ = '17-6-14 下午7:35'

import requests
import re

try:
    import cookielib
except:
    import http.cookiejar as cookielib


session = requests.session()
session.cookies = cookielib.LWPCookieJar(filename="cookies.txt")
try:
    session.cookies.load(ignore_discard = True)
except:
    print("Cookie 未能加载成功")

# 设置一个代理
agent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36"
# 设置requests的header
header = {
    "HOST" : "www.zhihu.com",
    "Referer" : "https://www.zhihu.com",
    "User-Agent" : agent,
}


# 通过个人中心页面返回状态吗来判断是否为登录状态
def is_login():
    inbox_url = "https://www.zhihu.com/inbox"
    response = session.get(inbox_url, headers=header, allow_redirects=False)

    if response.status_code != 200:
        return False
    else:
        return True
    pass



# 获取网站的"_xsrf"的值
def get_xsrf():
    response = session.get("https://www.zhihu.com", headers = header)

    match_obj = re.match('.*name="_xsrf" value="(.*?)"',response.text)
    if match_obj:
        return match_obj.group(1)
    else:
        return ""


def get_index():
    response = session.get("https://www.zhihu.com", headers=header)
    with open("index_page.html", "wb") as f:
        f.write(response.text.encode("utf-8"))
    print("ok")

# 模拟知乎登录
def zhihu_login(account, password):

    # 使用手机号码登录
    if re.match("^1\d{10}", account):
        print("手机号码登录")
        post_url = "https://www.zhihu.com/login/phone_num"
        post_data = {
            "_xsrf":get_xsrf(),
            "phone_num":account,
            "password":password,
        }
    # 使用邮箱账号登录
    elif "@" in account:
        print("邮箱方式登录")
        post_url = "https://www.zhihu.com/login/email"
        post_data = {
            "_xsrf":get_xsrf(),
            "email":account,
            "password":password,
        }

    response_text = session.post(post_url, data=post_data,headers=header)

    session.cookies.save()

    print("登录")

# get_index()
is_login()


