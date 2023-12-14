#! /usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2023/11/2919:44
# @File: async_spider.PY
import aiohttp
import asyncio
import datetime
import warnings
from asyncio.queues import Queue
from simpyder.__version__ import __VERSION__
from simpyder.utils import _get_logger
from lxml.etree import HTML

warnings.filterwarnings("ignore")  # 屏蔽废弃告警


class AsyncSpider(object):
    def __init__(self, name: str = "Simpyder", user_agent: str = f"Simpyder ver.{__VERSION__}",
                 interval: int = 0, concurrency: int = 8, log_level: str = "INFO"):
        """

        :param name:
        :param user_agent:
        :param interval: 间隔
        :param concurrency:  同时并发
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

    async def __update_proxy(self):
        if len(self.succeed_proxies) != 0:
            self.proxy = next(iter(self.succeed_proxies))
        else:
            try:
                self.proxy = await self.proxy_gener.__anext__()
            except Exception as e:
                self.logger.warning(f"没有可用的代理， Error: {e}")
                self.proxy = ""

    async def get(self, url, proxy='', retry=5):
        response = None
        for i in range(retry):
            try:
                response = await self.session.get(
                    url, headers=self.header, proxy=proxy if proxy else '', timeout=5
                )
                if 'content-type' in response.headers and 'html' in response.content_type:
                    response.xpath = HTML(await response.text()).xpath

                if response.content_type == 'application/json':
                    response.json_data = await response.json()

                if response.status != 200 or self.except_content_type is not None and response.content_type != self.except_content_type:
                    if proxy is not None:
                        await self.__update_proxy()
                        proxy = self.proxy
                    continue
                break
            except Exception as e:
                if not proxy:
                    await self.__update_proxy()
                    proxy = self.proxy
                continue
            break
        if response is not None and response.status == 200:
            self.succeed_proxies.add(proxy)
        else:
            self.succeed_proxies.discard(self.proxy)
            if proxy is not None:
                await self.__update_proxy()
        return response

    async def gen_url(self):
        self.logger.critical('未实现方法： gen_url()，无法开启爬虫任务')
        yield None

    async def parse(self, response):
        self.logger.critical('未实现方法: parse(response)，将直接返回Response对象')
        return response

    async def save(self, item):
        self.logger.critical('未实现方法: save(item)，将直接打印爬取内容。')
        return item

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

    async def crawl_one_url(self, url, proxy):
        try:
            self.logger.info(f"> Crawl a Url: {url}")
            if type(url) == str and url[:4] == 'http':
                self.logger.debug(f"下载数据： {url}")
                res = await self.get(url)
                if res is None:
                    self.logger.warning(f"下载数据失败 {url} {proxy}")
                else:
                    self.logger.debug(f"非URL直接返回")
                    res = url
                self._url_count += 1
                item = await self.parse(res)
                count = await self.save(item)
                self._item_count += count if type(count) == int else 1
                self.logger.debug(f'[Finished] Crawl a Url: {url}')
        except Exception as e:
            self.logger.exception(e)

    async def __crawl(self, crawl_sem, lock):
        async with crawl_sem:
            try:
                if not self.url_task_queue.empty():
                    await lock.acquire()
                    self.count += 1
                    try:
                        lock.release()
                        url = await self.url_task_queue.get()
                        await self.crawl_one_url(url, self.proxy)
                        self.url_task_queue.task_done()
                    finally:
                        await lock.acquire()
                        self.count += 1
                        lock.release()
                else:
                    await asyncio.sleep(10)

            except Exception as e:
                self.logger.exception(e)

    async def _run_crawler(self, i):
        try:
            crawl_sem = asyncio.Semaphore(self.concurrency)
            lock = asyncio.Lock()
            self.logger.info(f"Start Crawler: {i}")

            while self.finished is False or not self.url_task_queue.empty():
                await asyncio.sleep(0)
                async with crawl_sem:
                    asyncio.ensure_future(self.__crawl(crawl_sem, lock))

        except Exception as e:
            self.logger.exception(e)

    async def _add_url_to_queue(self):
        url_gener = self.gen_url()
        async for url in url_gener:
            self.logger.debug(f"Crawl Url: {url}")
            await self.url_task_queue.put(url)
            await asyncio.sleep(self.interval)

    async def _run(self):
        self.logger.info(f"Spider Task Start...")
        self.proxy = await self.proxy_gener.__anext__()
        self.url_task_queue = Queue(30)

        start_time = datetime.datetime.now()
        tasks = []
        print_log = asyncio.ensure_future(self._auto_print_log())
        self.logger.info(f"Create Crawl Tasks")
        crawl_task = asyncio.ensure_future(self._run_crawler(0))

        await self._add_url_to_queue()
        await asyncio.sleep(5)
        while not self.url_task_queue.empty() or self.count != 0:
            await asyncio.sleep(5)
        self.finished = True
        await crawl_task
        self.logger.critical(f"Simpyder 任务执行完毕")
        end_time = datetime.datetime.now()
        delta_time = end_time - start_time
        self.logger.critical("累计消耗时间： %s" % str(delta_time))
        self.logger.critical(f"累计爬取链接：{self._url_count}")
        self.logger.critical(f"累计生成对象： {self._item_count}")

        await print_log
        await self.session.close()

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
    test.concurrency = 64
    test.interval = 0


    async def g():
        for _ in range(1024):
            yield "https://www.baidu.com"


    test.gen_url = g


    async def parse(res):
        await asyncio.sleep(0.1)
        return "parsed item"


    test.parse = parse


    async def save(item):
        await asyncio.sleep(0.1)
        return 2


    test.save = save

    test.run()
