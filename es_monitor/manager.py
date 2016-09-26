#!/usr/bin/env python
# coding=utf-8

from oslo_config import cfg
from oslo_service import periodic_task

from es_monitor import log as logging

LOG = logging.getLogger(__name__)
CONF = cfg.CONF


class PeriodicTasks(periodic_task.PeriodicTasks):
    def __init__(self):
        super(PeriodicTasks, self).__init__(CONF)


class Manager(PeriodicTasks):

    def __init__(self, *args, **kwargs):
        super(Manager, self).__init__()

    def periodic_tasks(self, context, raise_on_error=False):
        """Tasks to be run at a periodic interval."""
        return self.run_periodic_tasks(context, raise_on_error=raise_on_error)

    def init_host(self):
        pass
