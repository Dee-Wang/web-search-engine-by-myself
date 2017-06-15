# -*- coding: utf-8 -*-
import scrapy
import json
import re


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['https://www.zhihu.com/']

    # 设置一个代理
    agent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36"
    # 设置requests的header
    header = {
        "HOST": "www.zhihu.com",
        "Referer": "https://www.zhihu.com",
        "User-Agent": agent,
    }

    def parse(self, response):
        """
        提取出HTML页面中的所有的URL，并且跟踪这些URL进行下一步的爬取
        如果提取的url中的格式位/question/xxx就下载之后直接进入解析函数
        :param response: 
        :return: 
        """
        all_urls = response.css("a")

    def parse_detail(self, response):
        pass


    def start_requests(self):
        return [scrapy.Request("https://www.zhihu.com/#signin", headers=self.header, callback=self.login)]

    def login(self, response):
        response_text = response.text
        match_obj = re.match('.*name="_xsrf" value="(.*?)"',response_text, re.DOTALL)
        xsrf = ''

        if match_obj:
            xsrf = (match_obj.group(1))

        if xsrf:
            post_url = "https://www.zhihu.com/login/phone_num",
            post_data = {
            "_xsrf": xsrf,
            "phone_num": "********",
            "password": "*******"
            }
            return [scrapy.FormRequest(
                url = post_url,
                formdata = post_data,
                headers = self.header,
                callback = self.check_login
            )]

    # 验证服务器返回的数据判断是否成功
    def check_login(self, response):
        text_json = json.loads(response.text)
        if "msg" in text_json and text_json["msg"]=="登录成功":
            for url in self.start_urls:
                yield scrapy.Request('https://www.zhihu.com/', dont_filter=True, headers=self.header)