# -*- coding: utf-8 -*-
import scrapy

import re
import datetime
import ArticleSpider

from scrapy.http import Request
from scrapy.loader import ItemLoader
from ArticleSpider.items import ArticleItemLoader

from urllib import parse
from ArticleSpider.items import JobBoleArticleItem
from ArticleSpider.utils.common import get_md5

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
        post_nodes = response.css("#archive .floated-thumb .post-thumb a")
        for post_node in post_nodes:
            image_url = post_node.css("img::attr(src)").extract_first("")
            post_url = post_node.css("::attr(href)").extract_first("")
            yield Request(url=parse.urljoin(response.url, post_url),meta = {"front_image_url":image_url}, callback=self.parse_detail)

        # # 提取下一页并交给scrapy进行下载
        # next_url = response.css('.next.page-numbers::attr(href)').extract_first("")
        # if next_url:
        #     yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_detail(self, response):
        """提取文章的具体字段"""

        article_item = JobBoleArticleItem()
        # 获取当前的文章的封面图
        fornt_image_url = response.meta.get("front_image_url", "")

        # 通过css选择器提取文章标题字段,这里还是以字符串形式存储
        title = response.css(".entry-header h1::text").extract_first("")

        # 获取当前的URL页面对应的文章的发表日期，以字符串形式存储
        post_date = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()').extract_first("").strip().replace("·"," ").strip()

        # 获取当前URL页面的文章的点赞数,以整型数存储
        praise_num = int(response.xpath("//span[contains(@class,'vote-post-up')]/h10/text()").extract_first(""))
        # praise_num = response.xpath("//span[contains(@class,'vote-post-up')]/h10/text()").extract_first("")
        # if praise_num:
        #     praise_num = int(praise_num)
        # else:
        #     praise_num = 0

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
        tags_list = response.css('.entry-meta-hide-on-mobile a::text').extract()
        # tags_list = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/a/text()').extract()
        tags_list = [element for element in tags_list if not element.strip().endswith("评论")]
        tags = ",".join(tags_list)

        article_item["url_object_id"] = get_md5(response.url)
        article_item["title"] = title
        # 因为存储到数据库中的发布时间是date的形式，所以要在这里将字符串的形式转化成date的形式
        try:
            post_date = datetime.datetime.strptime(post_date, "%Y/%m/%d").date()
        except Exception as e:
            post_date = datetime.datetime.now().date()

        # article_item["post_date"] = post_date
        # article_item["praise_num"] = praise_num
        # article_item["favor_num"] = favor_num
        # article_item["comments_num"] = comments_num
        # article_item["contant"] = contant
        # article_item["tags"] = tags
        # article_item["url"] = response.url
        # article_item["front_image_url"] = [fornt_image_url]
        
        item_loader = ArticleItemLoader(item=JobBoleArticleItem(), response=response)
        item_loader.add_css("title",".entry-header h1::text")
        item_loader.add_css("post_date","p.entry-meta-hide-on-mobile ::text" )
        item_loader.add_css("praise_num",".vote-post-up h10::text" )
        item_loader.add_css("favor_num", ".bookmark-btn::text")
        item_loader.add_css("comments_num", ".post-adds a  span::text")
        item_loader.add_css("contant", ".entry")
        item_loader.add_css("tags", ".entry-meta-hide-on-mobile a::text")
        item_loader.add_value("url", response.url)
        item_loader.add_value("front_image_url", [fornt_image_url])

        article_item = item_loader.load_item()

        yield article_item

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


