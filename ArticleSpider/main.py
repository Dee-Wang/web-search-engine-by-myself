# -*- coding: utf-8 -*-
__author__ = 'Dee'
__date__ = '17-5-31 上午10:23'

from scrapy.cmdline import execute

import sys
import os



# print(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# execute(["scrapy", "crawl", "jobbole"])
execute(["scrapy", "crawl", "zhihu"])