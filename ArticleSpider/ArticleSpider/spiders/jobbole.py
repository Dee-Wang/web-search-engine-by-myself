# -*- coding: utf-8 -*-
import scrapy

import re

from scrapy.http import Request
from urllib import parse

class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        """
        1. 获取文章列表页中的文章url并交给scrapy下载后进行解析
        2. 获取下一些的url并且交给scrapy进行下载，下载完成之后交给pass函数
        :param response: 
        :return: 
        """

        # 获取文章列表页中的文章url并交给scrapy下载后进行解析
        post_urls = response.css("#archive .floated-thumb .post-thumb a::attr(href)").extract()
        for post_url in post_urls:
            yield Request(url=parse.urljoin(response.url, post_url),callback=self.parse_detail)

        # 提取下一页并交给scrapy进行下载
        next_url = response.css('.next.page-numbers::attr(href)').extract_first("")
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)



    def parse_detail(self, response):
        """提取文章的具体字段"""
        
        # 通过css选择器提取文章标题字段,这里还是以字符串形式存储
        title = response.css(".entry-header h1::text").extract_first("")

        # 获取当前的URL页面对应的文章的发表日期，以字符串形式存储
        post_date = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()').extract_first("").strip().replace("·"," ").strip()

        # 获取当前URL页面的文章的点赞数,以整型数存储
        praise_num = int(response.xpath("//span[contains(@class,'vote-post-up')]/h10/text()").extract_first(""))

        # 获取当前URL页面的文章的收藏数,以整型数存储
        favor_num = response.xpath("//span[contains(@class,'bookmark-btn')]/text()").extract_first("")
        match_re1 = re.match(".*(\d+).*", favor_num)
        if match_re1:
            favor_num = int(match_re1.group(1))
        else:
            favor_num = 0

        # 获取当前URL页面的文章的评论数,以整型数存储
        # comments_num = int(re.match(".*(\d+).*", response.xpath("//div[@class='post-adds']/a/span/text()").extract_first("")).group(1))
        comments_num = response.xpath("//div[@class='post-adds']/a/span/text()").extract_first("")
        match_re2 = re.match(".*(\d+).*", comments_num)
        if match_re2:
            comments_num = int(match_re2.group(1))
        else:
            comments_num = 0

        # 获取正文的内容,因为正文处理比较复杂，所以先不处理，只是获取正文的所有的html代码
        contant = response.xpath('//div[@class="entry"]').extract_first("")

        # 获取文章的标签
        tags_list = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/a/text()').extract()
        tags_list = [element for element in tags_list if not element.strip().endswith("评论")]



        # # 获取当前的URL对应的页面的文章的标题,以字符串形式存储
        # title = response.xpath('//*[@id="post-111312"]/div[1]/h1/text()').extract_first("")
        # # 通过css选择器来提取文章的字符串形式的发布日期，其实在这里class的值是整个文件唯一的，所以省略掉元素名字也是可以的。
        # create_date_bycss1 = response.css("p.entry-meta-hide-on-mobile ::text").extract_first("").strip().replace("·"," ").strip()
        #
        # create_date_bycss2 = response.css(".entry-meta-hide-on-mobile ::text").extract_first("").strip().replace("·",
        #                                                                                                      " ").strip()
        #
        # # 另一种方法处理发布日期后面的点(使用了分片的函数，将数组的第一个元素默认情况下按照空格分成了两片，我们去除第一个元素就可以)
        # create_date_bycss3 = response.css("p.entry-meta-hide-on-mobile ::text").extract_first("").split()[0]
        #
        # # 使用css选择器来获取当前的文章的点赞数,使用int函数将结果转换成整型数的形式
        # praise_num_bycss = int(response.css(".vote-post-up h10::text").extract_first(""))
        #
        # # 这里留一个错误的例子，因为点赞数中的类的名字不止一个，所以使用"元素.class"的形式时会出错的
        # #praise_num_bycss_error = int(response.css("span.vote-post-up h10::text").extract_first(""))
        #
        # # 使用css选择器来获取当前文章的收藏数，并且转换成整型数的形式
        # favor_num_bycss = response.css(".bookmark-btn::text").extract_first("")
        # match_re1 = re.match(".*(\d+).*", favor_num_bycss)
        # if match_re1:
        #     favor_num_bycss = int(match_re1.group(1))
        # else:
        #     comments_num_bycss = 0
        #
        # # 使用css选择器来获取当前的文章的评论数并且转换成整型数的形式
        # # comments_num_bycss = response.css(".post-adds a  span::text").extract_first("")
        # comments_num_bycss = response.css('a[href="#article-comment"] span::text').extract_first("")
        # match_re1 = re.match(".*(\d+).*", comments_num_bycss)
        # if match_re1:
        #     comments_num_bycss = int(match_re1.group(1))
        # else:
        #     comments_num_bycss = 0
        #
        # # 使用css选择器获取正文的内容,因为正文处理比较复杂，所以先不处理，只是获取正文的所有的html代码
        # contant_bycss = response.css('.entry').extract_first("")
        #
        # # 使用css选择器获取文章的标签,用一个列表的形式存储并且展示
        # tags_list_bycss = response.css('.entry-meta-hide-on-mobile a::text').extract()
        # tags_list_bycss = [element for element in tags_list_bycss if not element.strip().endswith("评论")]

        pass
