#!/usr/bin/env python
# coding=utf-8

import json
from oslo_config import cfg

from es_monitor import log as logging
from es_monitor.utils.c2dict import class_to_dict

LOG = logging.getLogger(__name__)

node_info_opts = [
        cfg.StrOpt(
            'dtype_node_info',
            default='node_info',
            help="doc type for node info"),
        ]

CONF = cfg.CONF
CONF.register_opts(node_info_opts)


class NodeInfo(object):

    def __init__(self, line):
        '''
        Constructor
        :param line:
        terms = ["host",    "ip",   "heap_percent", "ram_percent",  "load", "node_role",    "master",   "name"]
        '''
        terms = line.split()
        self.name = terms[7]
        self.host = terms[0]
        self.ip = terms[1]
        self.heap_percent = terms[2]
        self.ram_percent = terms[3]
        self.load = terms[4]
        self.role = terms[5]
        self.master = terms[6]
        self.shards = 0
        self.disk_free_space = 0
        self.jvm_memory = 0
        self.documents = 0
        self.size_in_bytes = 0
        self.indices = 0
        self.total_shards = 0
        self.type = ""
        self.status = ""
        self.search_latency = 0
        self.indexing_latency = 0
        self.jvm_heap_usage = 0
        self.cpu_utilization = 0
        self.system_load_average = 0
        self.segment_count = 0

    def update_from_nodes_info(self, resp):
        LOG.debug("resp: %s" % resp)
        self.host = resp["host"]
        self.name = resp["name"]
        self.ip = resp["ip"]
        self.cversion = resp["version"]
        self.transport_address = resp["transport_address"]

    def update_from_nodes_stats(self, resp):
        LOG.debug("resp: %s" % resp)
        self.documents = resp["indices"]["docs"]["count"]
        self.size_in_bytes = resp["indices"]["store"]["size_in_bytes"]
        self.load = resp["os"]["load_average"]
        self.segment_count = resp["indices"]["segments"]["count"]
        self.mem_total_in_bytes = resp["os"]["mem"]["total_in_bytes"]
        self.mem_free_in_bytes = resp["os"]["mem"]["free_in_bytes"]
        self.mem_used_in_bytes = resp["os"]["mem"]["used_in_bytes"]
        self.jvm_mem_heap_used_in_bytes = resp["jvm"]["mem"]["heap_used_in_bytes"]
        self.jvm_mem_heap_max_in_bytes = resp["jvm"]["mem"]["heap_max_in_bytes"]

    def update_from_cat_nodes(self, resp):
        LOG.debug("resp: %s" % resp)
        pass

    def submit_info(self, es, index):
        LOG.debug("Enter into submit_info")
        body = json.dumps(class_to_dict(self))
        LOG.debug("body: %s" % body)
        es.index(index=index, doc_type=CONF.dtype_node_info, body=body)
