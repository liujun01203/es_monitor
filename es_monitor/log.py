#!/usr/bin/env python
# coding=utf-8

import inspect
import logging
import os
from logging.handlers import TimedRotatingFileHandler

from oslo_config import cfg


opts = [
    cfg.BoolOpt('debug',
                short='d',
                default=True,
                help='Print debugging output (set logging level to '
                     'DEBUG instead of default WARNING level).'),
    cfg.BoolOpt('verbose',
                short='v',
                default=True,
                help='Print more verbose output (set logging level to '
                     'INFO instead of default WARNING level).'),
    cfg.StrOpt('log-file',
               metavar='PATH',
               deprecated_name='logfile',
               help='(Optional) Name of log file to output to. '
                    'If no default is set, logging will go to stdout.'),
    cfg.IntOpt('log_interval',
               default=1,
               help='The interval time between two log files',
               ),
    cfg.IntOpt('log_backcount',
               default=7,
               help='The number of log files to reserved',
               ),
    cfg.StrOpt('log-dir',
               deprecated_name='logdir',
               default='/var/log/es_monitor',
               help='(Optional) The base directory used for relative '
                    '--log-file paths'),
]

CONF = cfg.CONF
CONF.register_cli_opts(opts)


def _get_binary_name():
    return os.path.basename(inspect.stack()[-1][1])


def _get_log_file_path(binary=None):
    logfile = CONF.log_file
    logdir = CONF.log_dir

    if logfile and not logdir:
        return logfile

    if logfile and logdir:
        return os.path.join(logdir, logfile)

    if logdir:
        binary = binary or _get_binary_name()
        return '%s.log' % (os.path.join(logdir, binary),)

    return None


def _get_formatter():
    date_fmt = "%Y-%m-%d %H:%M:%S"
    log_fmt = '%(asctime)s %(levelname)s %(name)s:%(lineno)d %(message)s'

    formatter = logging.Formatter(log_fmt, date_fmt)
    return formatter


def getLogger(name='unknown', version='unknown'):
    log_file = _get_log_file_path()
    formatter = _get_formatter()

    if log_file is None:
        handler = logging.StreamHandler()
    else:
        handler = TimedRotatingFileHandler(filename=log_file, when='D', interval=CONF.log_interval, backupCount=CONF.log_backcount)

    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.addHandler(handler)

    if CONF.debug:
        logger.setLevel(logging.DEBUG)
    elif CONF.verbose:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.WARNING)

    return logger
