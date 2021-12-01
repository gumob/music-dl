#!/usr/bin/env python
# coding: utf-8

import logging
import re
import sys

import colorama


class ColorizingStreamHandler(logging.StreamHandler):
    color_map = {
        logging.DEBUG: colorama.Fore.BLUE,
        logging.WARNING: colorama.Fore.YELLOW,
        logging.ERROR: colorama.Fore.RED,
        logging.CRITICAL: colorama.Back.RED,
    }

    def __init__(self, stream, color_map=None):
        logging.StreamHandler.__init__(self, colorama.AnsiToWin32(stream).stream)
        if color_map is not None:
            self.color_map = color_map

    @property
    def is_tty(self):
        isatty = getattr(self.stream, 'isatty', None)
        return isatty and isatty()

    def format(self, record):
        message = logging.StreamHandler.format(self, record)
        if self.is_tty:
            parts = [self.colorize(part, record) for part in message.split('\n', 1)]
            message = '\n'.join(parts)
        else:
            message = self.__remove_ansi(message)
        return message

    def colorize(self, message, record):
        try:
            return (self.color_map[record.levelno] + message +
                    colorama.Style.RESET_ALL)
        except KeyError:
            return message

    def __remove_ansi(self, s):
        ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
        return ansi_escape.sub('', s)


colorama.init(autoreset=True)
logging.basicConfig(filename='{}.log'.format('music_dl'))
logger = logging.getLogger('music_dl')
logger.setLevel(logging.DEBUG)
handler = ColorizingStreamHandler(sys.stdout)
handler_format = logging.Formatter('[music_dl] %(message)s')
handler.setFormatter(handler_format)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
