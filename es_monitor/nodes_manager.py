#!/usr/bin/env python
# coding=utf-8

from es_monitor import log as logging
from es_monitor.node import NodeInfo

LOG = logging.getLogger(__name__)


class NodesManager(object):
    def __init__(self, cluster_manager):
        '''
        Constructor
        '''
        self.nodes = set()
        metric_data = {}
        metric_data["timestamp"] = None
        self.metric_data = metric_data
        self.cluster_manager = cluster_manager
        self.check_interval = 0

    def set_timestamp(self, timestamp):
        metric_data = self.metric_data
        metric_data["timestamp"] = timestamp

    def set_check_interval(self, check_interval):
        self.check_interval = check_interval

    def update(self, context):
        if "timestamp" in context:
            self.set_timestamp(context["timestamp"])

        if "cat_indices" in context:
            self.update_from_cat_indices(context["cat_indices"])

        if "cat_nodes" in context:
            self.update_from_cat_nodes(context["cat_nodes"])

        if "cat_shards" in context:
            self.update_from_cat_shards(context["cat_shards"])

        if "cluster_stats" in context:
            self.update_from_cluster_stats(context["cluster_stats"])

        if "cluster_state" in context:
            self.update_from_cluster_state(context["cluster_state"])

        if "nodes_info"in context:
            self.update_from_nodes_info(context["nodes_info"])

        if "nodes_stats"in context:
            self.update_from_nodes_stats(context["nodes_stats"])

        if "indices_stats" in context:
            self.update_from_indices_stats(context["indices_stats"])

    def update_from_cluster_stats(self, resp):
        LOG.debug("resp: %s" % resp)
        pass

    def update_from_cluster_state(self, resp):
        LOG.debug("resp: %s" % resp)
        pass

    def update_from_indices_stats(self, resp):
        LOG.debug("resp: %s" % resp)
        pass

    def update_from_cat_indices(self, resp):
        pass

    def update_from_cat_shards(self, resp):
        '''
        :param resp:
        #state      node      shard prirep  docs index
        STARTED    Archenemy 0     p          5 .kibana
        UNASSIGNED           0     r            .kibana
        STARTED    Archenemy 0     p      35026 .marvel-es-2016.10.24
        UNASSIGNED           0     r            .marvel-es-2016.10.24
        STARTED    Archenemy 0     p      56935 .marvel-es-2016.10.26
        :return:
        '''
        LOG.debug("resp: %s" % resp)
        for node in self.nodes:
            node.update_from_cat_shards(resp)

    def update_from_cat_nodes(self, resp):
        '''
        :param resp:
        name      ip        load segments.count heap.percent heap.max
        Archenemy 127.0.0.1 0.19             41           13  990.7mb
        :return:
        '''
        LOG.debug("resp: %s" % resp)
        lines = resp.split('\n')
        for line in lines:
            line.strip()
            if line:
                node = NodeInfo(line, self)
                self.nodes.add(node)

    def update_from_nodes_info(self, resp):
        LOG.debug("resp: %s" % resp)
        nodes = resp["nodes"]
        for node in nodes.values():
            nodeinfo = self.get_node_info(node["name"])
            nodeinfo.update_from_nodes_info(node)

    def get_node_info(self, name):
        LOG.debug("name: %s" % name)
        for node in self.nodes:
            if name == node.metric_data["name"]:
                return node

    def update_from_nodes_stats(self, resp):
        LOG.debug("resp: %s" % resp)
        nodes = resp["nodes"]
        for node in nodes.values():
            node_info = self.get_node_info(node["name"])
            node_info.update_from_nodes_stats(node)

    def submit_info(self, es, index):
        for node in self.nodes:
            node.set_timestamp(self.metric_data["timestamp"])
            node.submit_info(es, index)
