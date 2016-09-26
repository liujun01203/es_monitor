#!/usr/bin/env python
# coding=utf-8

from oslo_config import cfg


def parse_args(argv, default_config_files=None):
    cfg.CONF(argv[1:],
             project='es_monitor',
             default_config_files=default_config_files)
