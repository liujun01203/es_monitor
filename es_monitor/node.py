#!/usr/bin/env python
# coding=utf-8

import json
from oslo_config import cfg

from es_monitor import log as logging

LOG = logging.getLogger(__name__)

node_info_opts = [
    cfg.StrOpt(
        'dtype_node_info',
        default='node_info',
        help="doc type for node info"
    ),
]

CONF = cfg.CONF
CONF.register_opts(node_info_opts)


class NodeInfo(object):

    def __init__(self, line, manager):
        '''
        Constructor
        :param line:
        '''
        #marvel mtric
        self.manager = manager
        metric_data = {}
        metric_data["name"] = ''
        metric_data["host"] = ''
        metric_data["ip"] = ''
        metric_data["documents"] = 0
        metric_data["data"] = 0  # size in bytes
        metric_data["disk_free_space"] = 0  # free capacity in bytes in fs
        metric_data["indices"] = 0
        metric_data["total_shards"] = 0

        self.last_search_query_total = 0
        self.current_search_query_total = 0
        self.last_search_query_time_in_millis = 0
        self.current_search_query_time_in_millis = 0
        metric_data["search_latency"] = 0.0  # size in ms

        self.last_indexing_total = 0
        self.current_indexing_total = 0
        self.last_indexing_time_in_millis = 0
        self.current_indexing_time_in_millis = 0
        metric_data["indexing_latency"] = 0.0  # size in ms

        metric_data["jvm_heap_usage"] = 0
        metric_data["cpu_utilization"] = 0
        metric_data["system_load_average"] = 0  # just like uptime: last 1 minutes cpu load average
        metric_data["segment_count"] = 0
        metric_data["timestamp"] = None
        self.metric_data = metric_data
        self.update_from_cat_nodes(line)

    def __eq__(self, other):
        try:
            return self.metric_data["name"] == other.metric_data["name"]
        except AttributeError:
            return False

    def __hash__(self):
        return hash(self.metric_data["name"])

    def set_timestamp(self, timestamp):
        metric_data = self.metric_data
        metric_data["timestamp"] = timestamp

    def reset_metrics(self):
        metric_data = self.metric_data
        metric_data["host"] = ''
        metric_data["ip"] = ''
        metric_data["documents"] = 0
        metric_data["data"] = 0  # size in bytes
        metric_data["disk_free_space"] = 0  # free capacity in bytes in fs
        metric_data["indices"] = 0
        metric_data["total_shards"] = 0
        metric_data["search_latency"] = 0.0  # size in ms
        metric_data["indexing_latency"] = 0.0  # size in ms
        metric_data["jvm_heap_usage"] = 0
        metric_data["cpu_utilization"] = 0
        metric_data["system_load_average"] = 0  # just like uptime: last 1 minutes cpu load average
        metric_data["segment_count"] = 0
        metric_data["timestamp"] = None

    def update_from_cat_shards(self, resp):
        '''
        :param resp:
        #state      node      shard prirep  docs index
        STARTED    Archenemy 0     p      35026 .marvel-es-2016.10.24
        UNASSIGNED           0     r            .marvel-es-2016.10.24
        :return:
        '''
        LOG.debug("resp: %s" % resp)
        lines = resp.split('\n')
        valid_state = ["STARTED", ]
        indices = set()
        metric_data = self.metric_data
        for line in lines:
            if len(line.strip()) == 0:
                continue

            terms = line.split()
            if terms[0] not in valid_state:
                continue

            if terms[1] != metric_data["name"]:
                continue

            indices.add(terms[5])
            metric_data["total_shards"] = metric_data["total_shards"] + 1
        metric_data["indices"] = len(indices)

    def update_from_cat_nodes(self, resp):
        '''
        :param resp:
        #name      ip        load segments.count heap.percent host
        Archenemy 127.0.0.1 0.19             41           13  127.0.0.1
        :return:
        '''
        LOG.debug("resp: %s" % resp)
        metric_data = self.metric_data
        terms = resp.split()
        metric_data["name"] = terms[0]
        metric_data["ip"] = terms[1]
        metric_data["system_load_average"] = float(terms[2])
        metric_data["segment_count"] = int(terms[3])
        metric_data["jvm_heap_usage"] = int(terms[4])
        metric_data["host"] = terms[5]

    def update_from_nodes_info(self, resp):
        LOG.debug("resp: %s" % resp)
        pass

    def update_from_nodes_stats(self, resp):
        LOG.debug("resp: %s" % resp)
        metric_data = self.metric_data
        metric_data["documents"] = resp["indices"]["docs"]["count"]
        metric_data["data"] = resp["indices"]["store"]["size_in_bytes"]
        metric_data["cpu_utilization"] = resp["process"]["cpu"]["percent"]
        metric_data["disk_free_space"] = resp["fs"]["total"]["free_in_bytes"]

        self.last_indexing_total = self.current_indexing_total
        self.current_indexing_total = resp["indices"]["indexing"]["index_total"]
        self.last_indexing_time_in_millis = self.current_indexing_time_in_millis
        self.current_indexing_time_in_millis = resp["indices"]["indexing"]["index_time_in_millis"]

        delta_in_minllis = self.current_indexing_time_in_millis - self.last_indexing_time_in_millis
        if self.last_indexing_total != 0 and delta_in_minllis != 0:
            metric_data["indexing_latency"] = delta_in_minllis * 1.0/(self.current_indexing_total - self.last_indexing_total)

        self.last_search_query_total = self.current_search_query_total
        self.current_search_query_total = resp["indices"]["search"]["query_total"]
        self.last_search_query_time_in_millis = self.current_search_query_time_in_millis
        self.current_search_query_time_in_millis = resp["indices"]["search"]["query_time_in_millis"]

        delta_in_minllis = self.current_search_query_time_in_millis - self.last_search_query_time_in_millis
        if self.last_search_query_total != 0 and delta_in_minllis != 0:
            metric_data["search_latency"] = delta_in_minllis * 1.0/(self.current_search_query_total - self.last_search_query_total)

    def submit_info(self, es, index):
        LOG.debug("Enter into submit_info")
        body = json.dumps(self.metric_data)
        LOG.debug("body: %s" % body)
        es.index(index=index, doc_type=CONF.dtype_node_info, body=body)
        self.reset_metrics()
