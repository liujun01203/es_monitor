#!/usr/bin/env python
# coding=utf-8

import sys

from es_monitor import config
from es_monitor import service


def main():
    config.parse_args(sys.argv)
    server = service.Service.create(binary='es_monitor')
    service.serve(server)
    service.wait()

if __name__ == "__main__":
    main()
