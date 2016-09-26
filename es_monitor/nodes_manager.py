#!/usr/bin/env python
# coding=utf-8

from es_monitor.entity import Entity
from es_monitor import log as logging
from es_monitor.node import NodeInfo

LOG = logging.getLogger(__name__)


class NodesManager(Entity):
    def __init__(self):
        '''
        Constructor
        '''
        self.nodes = []

    def update(self, context):
        if "timestamp" in context:
            self.timestamp = context["timestamp"]

        if "cat_indices" in context:
            self.update_from_cat_indices(context["cat_indices"])

        if "cat_nodes" in context:
            self.update_from_cat_nodes(context["cat_nodes"])

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

    def update_from_cat_nodes(self, resp):
        LOG.debug("resp: %s" % resp)
        lines = resp.split('\n')
        for line in lines:
            line.strip()
            if line:
                node = NodeInfo(line)
                node.timestamp = self.timestamp
                self.nodes.append(node)

    def update_from_nodes_info(self, resp):
        LOG.debug("resp: %s" % resp)
        nodes = resp["nodes"]
        for node in nodes.values():
            nodeinfo = self.get_node_info(node["name"])
            nodeinfo.update_from_nodes_info(node)

    def get_node_info(self, name):
        for node in self.nodes:
            if name == node.name:
                return node

    def update_from_nodes_stats(self, resp):
        LOG.debug("resp: %s" % resp)
        nodes = resp["nodes"]
        for node in nodes.values():
            node_info = self.get_node_info(node["name"])
            node_info.update_from_nodes_stats(node)

    def submit_info(self, es, index):
        for node in self.nodes:
            node.submit_info(es, index)
