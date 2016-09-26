#!/usr/bin/env python
# coding=utf-8

import os
import random
import sys
from oslo_config import cfg
from oslo_service import service
from oslo_utils import importutils

from es_monitor import log as logging

LOG = logging.getLogger(__name__)

service_opts = [
    cfg.BoolOpt('periodic_enable',
                default=True,
                help='Enable periodic tasks'),
    cfg.IntOpt('periodic_fuzzy_delay',
               default=0,
               help='Range of seconds to randomly delay when starting the'
                    ' periodic task scheduler to reduce stampeding.'
                    ' (Disable by setting to 0)'),
    cfg.StrOpt('monitor_manager',
               default='es_monitor.monitor_manager.MonitorManager',
               help='Full class name for the Manager for monitor'),
    ]

CONF = cfg.CONF
CONF.register_opts(service_opts)


class Service(service.Service):

    def __init__(self, binary=None, manager=None, periodic_enable=None,
                 periodic_fuzzy_delay=None, periodic_interval_max=None,
                 *args, **kwargs):
        '''
        Constructor
        :param binary:
        :param manager:
        :param periodic_enable:
        :param periodic_fuzzy_delay:
        :param periodic_interval_max:
        :param args:
        :param kwargs:
        '''
        super(Service, self).__init__()
        self.binary = binary
        self.manager_class_name = manager
        manager_class = importutils.import_class(self.manager_class_name)
        self.manager = manager_class(*args, **kwargs)
        self.periodic_enable = periodic_enable
        self.periodic_fuzzy_delay = periodic_fuzzy_delay
        self.periodic_interval_max = periodic_interval_max

    def start(self):
        '''
        :return:
        '''
        self.manager.init_host()
        if self.periodic_enable:
            if self.periodic_fuzzy_delay:
                initial_delay = random.randint(0, self.periodic_fuzzy_delay)
            else:
                initial_delay = None

            self.tg.add_dynamic_timer(
                self.periodic_tasks,
                initial_delay=initial_delay,
                periodic_interval_max=self.periodic_interval_max)

    def __getattr__(self, key):
        '''
        :param key:
        :return:
        '''
        manager = self.__dict__.get('manager', None)
        return getattr(manager, key)

    @classmethod
    def create(cls, binary=None, manager=None, periodic_enable=None,
               periodic_fuzzy_delay=None, periodic_interval_max=None):
        if not binary:
            binary = os.path.basename(sys.argv[0])
        if not manager:
            manager_cls = ('%s_manager' %
                           binary.rpartition('es_')[2])
            manager = CONF.get(manager_cls, None)
        if periodic_enable is None:
            periodic_enable = CONF.periodic_enable
        if periodic_fuzzy_delay is None:
            periodic_fuzzy_delay = CONF.periodic_fuzzy_delay

        service_obj = cls(binary, manager, periodic_enable,
                          periodic_fuzzy_delay, periodic_interval_max)

        return service_obj

    def periodic_tasks(self, raise_on_error=False):
        """Tasks to be run at a periodic interval."""
        ctxt = None
        return self.manager.periodic_tasks(ctxt, raise_on_error=raise_on_error)


_launcher = None


def serve(server, workers=None):
    global _launcher
    if _launcher:
        raise RuntimeError('serve() can only be called once')

    _launcher = service.launch(CONF, server, workers=workers)


def wait():
    _launcher.wait()
