#! /usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2023/11/3021:11
# @File: scheduler.PY
class Scheduler(object):
    def __init__(self, spiders=[]):
        super().__init__()
        self.spiders = spiders

    def run_spiders(self):
        for each_spider in self.spiders:
            each_spider.run()
