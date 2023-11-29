#! /usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2023/11/2919:58
# @File: utils.PY
import logging
from simpyder.__version__ import __VERSION__

DEFAULT_UA = f"Simpyder {__VERSION__}"
FAKE_UA = "Mozilla/5.0 (Windows NT 10.0 Win64 x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 " \
          "Safari/537.36"

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

"""
The background is set with 40 plus th number of the color, 
and the foreground with 30.
"""

# These are the sequences nedd to get colored output.
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"

COLORS = {"WARNING": YELLOW,
          "INFO": CYAN,
          "DEBUG": BLUE,
          "CRITICAL": YELLOW,
          "ERROR": RED}


def formatter_message(message: str, use_color: bool = True):
    """

    :param message:
    :param use_color:
    :return:
    """
    if use_color:
        message = message.replace("$RESET", RESET_SEQ).replace("$BOLD", BOLD_SEQ)
    else:
        message = message.replace("$RESET", "").replace("$BOLD", "")

    return message


class ColoredFormatter(logging.Formatter):
    def __init__(self, msg, use_color: bool = True):
        logging.Formatter.__init__(self, msg)
        self.use_color = use_color

    def format(self, record):
        level_name = record.levelname
        if self.use_color and level_name in COLORS:
            level_name_color = COLOR_SEQ % (30 + COLORS[level_name]) + level_name + RESET_SEQ

            record.levelname = level_name_color

        return logging.Formatter.format(self, record)


class ColoredLogger(logging.Logger):
    FORMAT = "[%(asctime)s] [%(levelname)s] @ %(name)s: %(message)s"
    COLOR_FORMAT = formatter_message(FORMAT, True)

    def __init__(self, name):
        """

        :param name:
        """
        logging.Logger.__init__(self, name, logging.INFO)
        color_formatter = ColoredFormatter(self.COLOR_FORMAT)
        console = logging.StreamHandler()
        console.setFormatter(color_formatter)
        self.addHandler(console)

        return


def _get_logger(name: str, level: str = "INFO"):
    """
    get logger
    :param name:
    :param level:
    :return:
    """
    logging.setLoggerClass(ColoredLogger)
    logger = logging.getLogger(name)
    logger.setLevel(level)

    return logger
