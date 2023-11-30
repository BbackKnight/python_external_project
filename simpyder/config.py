#! /usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2023/11/2921:00
# @File: config.PY
from simpyder.utils import DEFAULT_UA


class SimpyderConfig(object):
    COOKIE = ""
    DOWNLOAD_INTERVAL = 0
    HEADERS = None
    LOG_LEVEL = "INFO"
    PARSE_THREAD_NUMER = 8
    USER_AGENT = DEFAULT_UA
