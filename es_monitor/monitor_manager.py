#!/usr/bin/env python
# coding=utf-8

import time
from oslo_config import cfg
from oslo_service import periodic_task

from es_monitor import manager
from es_monitor import log as logging
from es_monitor.cluster_manager import ClusterManager
from template import default_template

LOG = logging.getLogger(__name__)


es_monitor_opts = [
    cfg.IntOpt(
        'check_interval',
        default=15,
        help='Interval that between get metrics.'
    ),
    cfg.ListOpt(
        'monitor_es_hosts',
        default=['localhost:9200'],
        help="ES Cluster to monitor"
    ),
    cfg.ListOpt(
        'write_to_es_hosts',
        default=['localhost:9200'],
        help="ES Cluster write metrics to"
    ),
    cfg.StrOpt(
        'index_name',
        default='.monitor',
        help='Index name write to'
    ),
    cfg.BoolOpt(
        'update_template',
        default=True,
        help="Whether update template for .monitor-*",
    ),
]

CONF = cfg.CONF
CONF.register_opts(es_monitor_opts)


class MonitorManager(manager.Manager):
    def __init__(self, monitor_es_hosts=None, write_to_es_hosts=None, *args, **kwargs):
        '''
        Constructor
        :param monitor_es_hosts:
        :param write_to_es_hosts:
        :param args:
        :param kwargs:
        '''
        super(MonitorManager, self).__init__(*args, **kwargs)
        self.monitor_cluster_manager = ClusterManager(hosts=CONF.monitor_es_hosts)
        self.monitor_cluster_manager.setup_write_to_es(hosts=CONF.write_to_es_hosts)
        self.monitor_cluster_manager.set_check_interval(CONF.check_interval)
        if CONF.update_template:
            self.monitor_cluster_manager.update_template(default_template)

    def update_index_name(self):
        current_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        self.index_name = '-'.join([CONF.index_name, current_date])

    @periodic_task.periodic_task(spacing=CONF.check_interval, run_immediately=True)
    def update_info(self, context):
        LOG.info("Enter into update_info")
        try:
            self.update_index_name()
            self.monitor_cluster_manager.update_info()
            self.monitor_cluster_manager.submit_info(self.index_name)
        except Exception as e:
            LOG.exception(e)

    def init_host(self):
        LOG.debug("Enter into init_host")
