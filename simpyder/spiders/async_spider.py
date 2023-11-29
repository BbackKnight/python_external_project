#! /usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2023/11/2919:44
# @File: async_spider.PY
import aiohttp
import asyncio
from asyncio.queues import Queue
from simpyder.__version__ import __VERSION__
from simpyder.utils import _get_logger


class AsyncSpider(object):
    def __init__(self, name: str = "Simpyder", user_agent: str = f"Sompyder ver.{__VERSION__}", interval: int = 0,
                 concurrency: int = 8, log_level: str = "INFO"):
        """

        :param name:
        :param user_agent:
        :param interval:
        :param concurrency:
        :param log_level:
        """
        self.count = 0
        self.finished = False
        self.log_interval = 5
        self.name = name
        self.succeed_proxies = set()
        self.retry = 5
        self.user_agent = user_agent
        self.concurrency = concurrency
        self.interval = interval
        self.log_level = log_level
        self.proxy = ""
        self._url_count = 0
        self._item_count = 0
        self_statistic = 0
        self.except_content_type = None
        self.header = {'user_agent': self.user_agent}
        self.session = aiohttp.ClientSession()

    def run(self):
        """

        :return:
        """
        self.logger = _get_logger(f"{self.name}", self.log_level)
        print("""\033[0;32m
        _____ _  Author: Jannchie         __
  / ___/(_)___ ___  ____  __  ______/ /__  _____
  \__ \/ / __ `__ \/ __ \/ / / / __  / _ \/ ___/
 ___/ / / / / / / / /_/ / /_/ / /_/ /  __/ /
/____/_/_/ /_/ /_/ .___/\__, /\__,_/\___/_/
                /_/    /____/  version: {}\033[0m """.format(__VERSION__))
        self.logger.critical(f"user_agent: {self.user_agent}")
        self.logger.critical(f"concurrency: {self.concurrency}")
        self.logger.critical(f"interval: {self.interval}")



if __name__ == '__main__':
    test = AsyncSpider()
    test.run()