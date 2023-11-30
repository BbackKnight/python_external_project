#! /usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2023/11/2919:44
# @File: async_spider.PY
import aiohttp
import asyncio
import datetime
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
        self._statistic = []
        self.except_content_type = None
        self.header = {'user_agent': self.user_agent}
        self.session = aiohttp.ClientSession()

    async def gen_proxy(self):
        while True:
            yield ""

    async def _print_log(self):
        self._statistic.append(
            {
                'url_count': self._url_count,
                'item_count': self._item_count,
                'time': datetime.datetime.now()
            }
        )
        if len(self._statistic) > 10:
            self._statistic = self._statistic[1:10]

        delta_url_count = self._statistic[-1]['url_count'] - self._statistic[0]['url_count']
        delta_item_count = self._statistic[-1]['url_count'] - self._statistic[0]['url_count']
        delta_seconds = (self._statistic[-1]['time'] - self._statistic[0]['time']).seconds
        url_rate = 0 if delta_seconds == 0 else delta_url_count / (delta_seconds / 60)
        item_rate = 0 if delta_seconds == 0 else delta_item_count / (delta_seconds / 60)

        loading = (f"[限速基线： {int(url_rate / (60 / self.interval) * 100)} %]"
                   if self.interval != 0 else "")
        self.logger.info(f"已经爬取{self._url_count}个链接【{int(url_rate)}/min】,"
                         f"共产生{self._item_count}个对象({int(item_rate)}/min) {loading}")

    async def _auto_print_log(self):
        self._last_url_count = 0
        self._last_item_count = 0
        while self.finished is False:
            await self._print_log()
            await asyncio.sleep(self.log_interval)

    async def _run(self):
        self.logger.debug(f"Spider Task Start...")
        self.proxy = await self.proxy_gener.__anext__()
        self.url_task_queue = Queue(30)

        start_time = datetime.datetime.now()
        tasks = []
        print_log = asyncio.ensure_future(self._auto_print_log())

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
        self.proxy_gener = self.gen_proxy()
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self._run())
        self.loop.close()


if __name__ == '__main__':
    test = AsyncSpider()
    test.run()
