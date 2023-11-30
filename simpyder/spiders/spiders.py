#! /usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2023/11/2920:57
# @File: spiders.PY
from time import sleep
import threading
import queue
import requests
from requests.adapters import HTTPAdapter
from lxml.etree import HTML
from simpyder.config import SimpyderConfig
import datetime
import socket
from simpyder.config import SimpyderConfig
from simpyder.utils import _get_logger
from simpyder.__version__ import __VERSION__


class Spider(object):
    def __init__(self, name: str = "Simpyder", gen_url=None, parse=None, save=None, config=SimpyderConfig()):
        """

        :param name:
        :param gen_url:
        :param parse:
        :param save:
        :param config:
        """
        # 配置session, 服用TCP连接
        self.session = requests.session()
        self.session.mount("http://", HTTPAdapter(max_retries=3))
        self.session.mount("https://", HTTPAdapter(max_retries=3))

        # 载入配置
        self.config = config

        # 载入主线程日志记录
        self.logger = _get_logger(f"{name} - main-thread", self.config.LOG_LEVEL)

        # 构造函数组装
        self.assemble(gen_url, parse, save)

        self.QUEUE_LEN = self.config.PARSE_THREAD_NUMER * 2
        self.url_queue = queue.Queue(self.QUEUE_LEN)
        self.item_queue = queue.Queue(self.QUEUE_LEN)
        self.except_queue = queue.Queue(1)
        self.queueLock = threading.Lock()
        self.threads = []
        self.name = name
        self._saving = True

    def __apply_config(self):
        """
        应用配置
        :return:
        """
        if self.config.HEADERS is None:
            self.headers = {"cookies": self.config.COOKIE,
                            "user-Agent": self.config.USER_AGENT}
        else:
            self.headers = self.config.HEADERS
        self.PARSE_THREAD_NUMER = self.config.PARSE_THREAD_NUMER

        if len(self.config.USER_AGENT) < 30:
            self.logger.critical(f"使用User-Agent: {self.config.USER_AGENT}")
        else:
            self.logger.critical(f"使用User-Agent: {self.config.USER_AGENT[:30]}...")
        self.logger.critical(f"使用COOKIE: {self.config.COOKIE}")
        self.logger.critical(f"线程数： {self.config.PARSE_THREAD_NUMER}")

    def assemble(self, gen_url=None, parse=None, save=None, config: SimpyderConfig = SimpyderConfig()):
        """
        构造函数
        :param gen_url:
        :param parse:
        :param save:
        :param config:
        :return:
        """
        if gen_url is not None:
            self.gen_url = gen_url
        if parse is not None:
            self.parse = parse
        if save is not None:
            self.save = save
        self.set_config(config)

    def set_config(self, config: SimpyderConfig):
        """
        设置配置
        :param config:
        :return:
        """
        self.config = config

    def run(self):
        """
        运行
        :return:
        """
        self.start_time = datetime.datetime.now()
        self._finish = False
        print(
            """
                   _____ _  Author: Jannchie         __         
                  / ___/(_)___ ___  ____  __  ______/ /__  _____
                  \__ \/ / __ `__ \/ __ \/ / / / __  / _ \/ ___/
                 ___/ / / / / / / / /_/ / /_/ / /_/ /  __/ /    
                /____/_/_/ /_/ /_/ .___/\__, /\__,_/\___/_/     
                                /_/    /____/   version: {}      
    
    
                    """.format(__VERSION__)
        )

        self.__apply_config()

if __name__ == '__main__':
    test_spider = Spider()
    test_spider.run()