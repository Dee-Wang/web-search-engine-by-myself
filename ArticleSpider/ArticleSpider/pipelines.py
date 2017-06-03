# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json
import MySQLdb
import MySQLdb.cursors

from twisted.enterprise import adbapi

from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter


class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item


# 保存JSON的pipeline,分成打开文件，写入文件，写完之后关掉文件
class JsonwithencodingPipeline(object):
    def __init__(self):
        # 传入codecs.open()函数的三个参数，第一个要打开的JSON文件，第二个参数表示的是权限，"w"表示可以写入，第三个参数是文件的编码方式，这里以utf-8编码编码方式存储
        self.file = codecs.open('article.json', 'w', encoding="utf-8")

    # """
    # 将item写入到文件中，这里使用到了json.dumps()函数将items转换成一个字符串，但是json接收参数是字典类型的，所以我们要先将item转换成字典类型.
    # 然后第二个参数一定要设置成False，否则出现中文等的时候可能会出错。
    # """
    def process_item(self,item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False)+"\n"
        self.file.write(lines)
        return item

    # 我们调用这个函数到什么时候结束呢，这里设置一个spider_closed的信号量，自己将这个文件给关闭。
    def spider_closed(self, spider):
        self.file.close()


# 链接数据库，将爬取道德内容存储到数据库中
class MysqlPipeline(object):
    def __init__(self):
        # 首先要连接数据库,connect()的参数分别是root, user_name, mysql pwd, datebase_name. 字符集，以及是否使用Unicode编码
        self.conn = MySQLdb.connect('localhost', 'root', '123456', 'article_spider', charset='utf8', use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self,item, spider):
        # 在sql语句中，"%s"是占位符，用来占住位置，方便接下来传参数
        insert_sql = """
            insert into jobbolearticle(title, post_date, url, favor_num, 
                                       comments_num, praise_num, tags,url_object_id, front_image_url, contant)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,%s)
        """
        self.cursor.execute(insert_sql, (item["title"], item["post_date"], item["url"],
                                         item["favor_num"], item["comments_num"],
                                         item["praise_num"],item["tags"],item["url_object_id"],
                                         item["front_image_url"][0], item["contant"]))
        # 为什么最后要commit呢？这里有一个坑，一开始写成了cursor.commit，但是出错了，改成conn试一试。
        self.conn.commit()
        # return item



# 调用scrapy提供的json export到处json文件
class JsonExpoterPipeline(object):
    def __init__(self):
        self.file = open('articleexport.json', 'wb') # 第一个参数是要打开的文件，第二个参数是打开的方式wb这里代表的是二进制的方式
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.exporter.start_exporting() # 开始导入

    def close_spider(self, spider):
        self.exporter.finish_exporting() # 完成导入
        self.file.close() # 将文件关掉

    # 有个疑问，这个函数是做什么的呢？
    """
    process_item(item, spider)
    每一个item管道组件都会调用该方法，并且必须返回一个item对象实例或raise DropItem异常。
    被丢掉的item将不会在管道组件进行执行此外，我们也可以在类中实现以下方法
    """
    def process_item(self,item, spider):
        self.exporter.export_item(item)
        return item


# 定制自己的pipeline
class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        for ok, value in results:
            image_field_path = value["path"]
        item["front_image_path"] = image_field_path

        return item
