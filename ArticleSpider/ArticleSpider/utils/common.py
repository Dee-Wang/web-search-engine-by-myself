# -*- coding: utf-8 -*-
__author__ = 'Dee'
__date__ = '17-6-2 下午5:03'

import hashlib


def get_md5(url):
    if isinstance(url, str):
        url = url.encode("utf-8")
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest() # 抽取摘要


if __name__ == "__main__":
    print(get_md5("http://www.jobbole.com/"))
