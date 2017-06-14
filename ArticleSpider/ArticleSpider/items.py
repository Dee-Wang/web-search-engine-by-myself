# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import datetime
import re

from scrapy.loader.processors import MapCompose, TakeFirst, Join
from scrapy.loader import ItemLoader


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


# 在一些字段的值后面添加自己想做的标记
def addjobbole(value):
    return value + "-Dee"


# 将日期类的字段，从字符串形式转换成为日期形式
def date_convert(value):
    # 因为存储到数据库中的发布时间是date的形式，所以要在这里将字符串的形式转化成date的形式
    try:
        post_date = datetime.datetime.strptime(value, "%Y/%m/%d").date()
    except Exception as e:
        post_date = datetime.datetime.now().date()

    return post_date


# 获取收藏数/评论数/点赞数，并且转换成整形术的方式传入item
def int_convert(value):
    match_re = re.match(".*(\d+).*", value)
    if match_re:
        value = int(match_re.group(1))
    else:
        value = 0

    return value


# # 查看爬取到的tags中是否包含字符串“评论”
# def find_comment(value):
#     match_re = re.search(".*(\d+)"+"评论", value)
#     if match_re:
#         return value


# 去除掉标签中的包含字符串"评论"的字符串
def clean_comment(value):
    if "评论" in value:
        return ""
    else:
        return value



# 因为我们向settings.py文件中传递的front_image_url是一个列表，但是这里都是用Takefirst得到的是字符串
# 所以我们要使用新的方式覆盖掉默认的output_processor，返回一个列表类型的值
def return_value(value):
    return value


# 自定义自己的ItemLoader
class ArticleItemLoader(ItemLoader):
    # 设置默认的是取第一个元素
    default_output_processor = TakeFirst()


# 定义JobBoleArticleItem的Item
class JobBoleArticleItem(scrapy.Item):
    title = scrapy.Field(
        # input_processor = MapCompose(addjobbole)
        input_processor = MapCompose(lambda x:x + "-jobbole",addjobbole),
    )
    post_date = scrapy.Field(
        input_processor=MapCompose(date_convert),
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    praise_num = scrapy.Field(
        input_processor=MapCompose(int_convert)
    )
    favor_num = scrapy.Field(
        input_processor=MapCompose(int_convert)
    )
    comments_num = scrapy.Field(
        input_processor=MapCompose(int_convert)
    )
    contant = scrapy.Field()
    tags = scrapy.Field(
        input_processor=MapCompose(clean_comment),
        # 因为本省使用css selector获得的就是一个list，而且我们本身要获得的也是一个list类型，所以在这里不用取list的第一个元素
        output_processor = Join(","),
    )
    front_image_url = scrapy.Field(
        output_processor = MapCompose(return_value)
    )
    front_image_path = scrapy.Field()

