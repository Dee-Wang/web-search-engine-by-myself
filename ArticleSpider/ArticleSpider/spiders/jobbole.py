# -*- coding: utf-8 -*-
import scrapy

from scrapy.http import Request
from urllib import parse

from ArticleSpider.items import ArticleItemLoader, JobBoleArticleItem


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

        # 提取下一页并交给scrapy进行下载
        next_url = response.css('.next.page-numbers::attr(href)').extract_first("")
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)
    # 提取文章的具体的字段并且使用ItemLoader竟得到的数据存储到Item中
    def parse_detail(self, response):
        """提取文章的具体字段"""

        # 获取当前的文章的封面图
        fornt_image_url = response.meta.get("front_image_url", "")
        
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



