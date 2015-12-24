#!/usr/bin/env python

from inspect import getframeinfo
from inspect import stack
from threading import Lock
from threading import Event
from threading import Thread
from time import clock
from time import sleep
from weakref import ref
from colorama import Fore
from colorama import Style
from colorama import init as colorama_init
from enum import IntEnum

__copyright__ = "Copyright 2015 The Paladin's Forge"
__license__ = "MIT"
__email__ = "ThePaladinsForge@gmail.com"
__version__ = "1.0"
__status__ = "Development"


class LogLevel(IntEnum):
    VERBOSE = 6,
    DEBUG = 5,
    INFO = 4,
    WARNING = 3,
    ERROR = 2,
    CRITICAL = 1,
    OFF = 0


class _LiteLog(object):
    def __init__(self, logger_ref, log_level=LogLevel.VERBOSE):
        self._logger_ref = logger_ref
        self._output_level = log_level

    def verbose(self, msg):
        if self._output_level >= LogLevel.VERBOSE:
            self._enqueue(LogLevel.VERBOSE, clock(), LiteLogger.get_caller(), msg)

    def debug(self, msg):
        if self._output_level >= LogLevel.DEBUG:
            self._enqueue(LogLevel.DEBUG, clock(), LiteLogger.get_caller(), msg)

    def info(self, msg):
        if self._output_level >= LogLevel.INFO:
            self._enqueue(LogLevel.INFO, clock(), LiteLogger.get_caller(), msg)

    def warning(self, msg):
        if self._output_level >= LogLevel.WARNING:
            self._enqueue(LogLevel.WARNING, clock(), LiteLogger.get_caller(), msg)

    def error(self, msg):
        if self._output_level >= LogLevel.ERROR:
            self._enqueue(LogLevel.ERROR, clock(), LiteLogger.get_caller(), msg)

    def critical(self, msg):
        if self._output_level >= LogLevel.CRITICAL:
            self._enqueue(LogLevel.CRITICAL, clock(), LiteLogger.get_caller(), msg)

    def _enqueue(self, log_level, ts, caller, msg):
        logger = self._logger_ref()
        if logger:
            logger.enqueue_msg(log_level, ts, caller, msg)


class LiteLogger(object):
    """ class documentation """
    INSTANCE = None

    def __new__(cls, *args, **kwargs):
        if cls.INSTANCE is None:
            assert cls == LiteLogger, "%s can not derive from SimpleLogger class." % cls.__name__
            return object.__new__(cls, args, kwargs)
        else:
            return cls.INSTANCE()  # INSTANCE is a ref

    def __init__(self, enable_threading=False):
        if LiteLogger.INSTANCE is None:
            colorama_init()
            LiteLogger.INSTANCE = ref(self)

            self._lock = Lock()
            from random import random
            self.id = random()
            self._msg_queue = []
            self._color = False
            self._output_level = LogLevel.INFO
            self._thread_shutdown = Event()
            self._thread = Thread(target=self._thread_write_messages)
            if enable_threading:
                self.set_threading(True)

    def __repr__(self):
        return str()

    def shutdown(self):
        # Ensure threading is off and remove reference to provide proper class cleanup
        self.set_threading(False)
        LiteLogger.INSTANCE = None

    @staticmethod
    def get_caller():
        s = stack()[2]
        parse_len = 25
        caller = getframeinfo(s[0])
        full_file_name = "{}:{}".format(caller.filename, caller.lineno)
        if len(full_file_name) > parse_len:
            file_name = "...{}".format(full_file_name[-parse_len + 3:])
        else:
            fmt_str = "{{0:>{}}}".format(parse_len)
            file_name = fmt_str.format(full_file_name)
        return file_name

    def get_log(self, log_level=LogLevel.INFO):
        return _LiteLog(ref(self), log_level)

    def set_output_level(self, level=LogLevel.INFO):
        self._output_level = level

    def set_threading(self, active):
        if active is True:
            self._enable_threading()
        else:
            if self._thread.is_alive():
                self._disable_threading()

    def set_color(self, active):
        if active is True:
            self._enable_color()
        else:
            self._disable_color()

    def write_messages(self):
        with self._lock:
            msg_list, self._msg_queue = self._msg_queue, []

        for msg in msg_list:
            print(self._format(*msg))

    def enqueue_msg(self, log_level, ts, caller, msg):
        if log_level <= self._output_level:
            msg_obj = (log_level, ts, caller, msg)
            with self._lock:
                self._msg_queue.append(msg_obj)

    def _thread_write_messages(self):
        while not self._thread_shutdown.is_set():
            sleep(.0001)
            self.write_messages()

    def _enable_threading(self):
        self._thread_shutdown.clear()
        self._thread = Thread(target=self._thread_write_messages)
        self._thread.setDaemon(True)
        self._thread.start()

    def _disable_threading(self):
        self._thread_shutdown.set()
        self._thread.join()
        self.write_messages()

    def _enable_color(self):
        self._color = True

    def _disable_color(self):
        self._color = False

    def _format(self, log_level, time_stamp, caller, msg):
        msg = str(msg)
        log_name = "INVALID"
        log_name_prefix = ""
        log_name_suffix = ""
        if log_level == LogLevel.VERBOSE:
            log_name = "VERBOSE"
            if self._color:
                log_name_prefix = Fore.WHITE
                log_name_suffix = Style.RESET_ALL
        elif log_level == LogLevel.DEBUG:
            log_name = "DEBUG"
            if self._color:
                log_name_prefix = Fore.WHITE
                log_name_suffix = Style.RESET_ALL
        elif log_level == LogLevel.INFO:
            log_name = "INFO"
            if self._color:
                log_name_prefix = Fore.WHITE
                log_name_suffix = Style.RESET_ALL
        elif log_level == LogLevel.WARNING:
            log_name = "WARNING"
            if self._color:
                log_name_prefix = Fore.YELLOW
                log_name_suffix = Style.RESET_ALL
        elif log_level == LogLevel.ERROR:
            log_name = "ERROR"
            if self._color:
                log_name_prefix = Fore.RED
                log_name_suffix = Style.RESET_ALL
        elif log_level == LogLevel.CRITICAL:
            log_name = "CRITICAL"
            if self._color:
                log_name_prefix = "{}{}".format(Fore.RED, Style.BRIGHT)
                log_name_suffix = Style.RESET_ALL

        header = "{}{:<8}{} : {} : {{}}".format(log_name_prefix, log_name, log_name_suffix, caller)
        next_line = "\n{}{{}}".format(" " * len("{:<8} : {} : ".format(log_name, caller)))
        output = ""
        for idx, msg_part in enumerate(msg.split("\n")):
            if idx == 0:
                output += header.format(msg_part)
            else:
                output += next_line.format(msg_part)

        return output
