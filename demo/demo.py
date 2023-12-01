#! /usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2023/12/111:07
# @File: demo.PY
from simpyder.spiders.spiders import Spider
from simpyder.config import SimpyderConfig


def gen_url():
    for each_id in range(100):
        yield f"https://www.bilibili.com/video/av{each_id}"


def parse(response):
    return response.xpath('//meta[@name="title"]/@content')[0]


def save(item):
    print(item)


if __name__ == '__main__':
    s1 = Spider("Bilibili title spider", gen_url, parse, save)
    sc = SimpyderConfig()
    sc.COOKIE = 'example:value;'
    sc.USER_AGENT = 'my user agent'
    s1.assemble(gen_url=gen_url, parse=parse, save=save, config=sc)
    s1.run()