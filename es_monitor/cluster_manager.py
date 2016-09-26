#!/usr/bin/env python
# coding=utf-8

from elasticsearch import Elasticsearch
import time

from es_monitor.nodes_manager import NodesManager
from es_monitor.indices_manager import IndicesManager
from es_monitor.cluster import ClusterInfo
from es_monitor import log as logging
from es_monitor import exception

LOG = logging.getLogger(__name__)


class ClusterManager(object):
    """
    pass
    """

    def __init__(self, hosts=None, transport_class=None, **kwargs):
        '''
        Constructor
        :param hosts:
        :param transport_class:
        :param kwargs:
        '''
        self.es = Elasticsearch(hosts=hosts)
        self.indices = self.es.indices
        self.cluster = self.es.cluster
        self.cat = self.es.cat
        self.nodes = self.es.nodes
        self.indices_manager = IndicesManager()
        self.nodes_manager = NodesManager()
        self.cluster_info = ClusterInfo()

    def setup_write_to_es(self, hosts=None, transport_class=None, **kwargs):
        self.write_to_es = Elasticsearch(hosts=hosts)

    def update_template(self, template):
        self.write_to_es.indices.put_template(".monitor", body=template)

    def update_info(self):
        LOG.debug("Enter into update_info")
        self.get_info_from_api()
        self.cluster_info_update()
        self.indices_info_update()
        self.nodes_info_update()

    def get_info_from_api(self):
        LOG.debug("Enter into get_info_from_api")
        context = {}
        #self.timestamp = time.strftime('%Y-%m-%d %H:%M:%S %Z', time.localtime (time.time()))
        self.timestamp = int(time.time())
        context["timestamp"] = self.timestamp

        try:
            context["cat_health"] = self.cat.health()
        except:
            raise exception.CatHealthException()

        try:
            context["cat_count"] = self.cat.count()
        except:
            raise exception.CatCountException()

        try:
            context["cat_indices"] = self.cat.indices()
        except:
            raise exception.CatIndicesException()

        try:
            context["cat_nodes"] = self.cat.nodes()
        except:
            raise exception.CatNodesException()

        try:
            context["cluster_stats"] = self.cluster.stats()
        except:
            raise exception.ClusterStatsException()

        try:
            context["cluster_state"] = self.cluster.state()
        except:
            raise exception.ClusterStateException()

        try:
            context["indices_stats"] = self.indices.stats()
        except:
            raise exception.IndicesStatsException()

        try:
            context["nodes_info"] = self.nodes.info()
        except:
            raise exception.NodesInfoException()

        try:
            context["nodes_stats"] = self.nodes.stats()
        except:
            raise exception.NodesStatsException()

        self.context = context

    def cluster_info_update(self):
        LOG.debug("Enter into cluster_info_update")
        self.cluster_info.update(self.context)

    def indices_info_update(self):
        LOG.debug("Enter into indices_info_update")
        self.indices_manager.update(self.context)

    def nodes_info_update(self):
        LOG.debug("Enter into nodes_info_update")
        self.nodes_manager.update(self.context)

    def submit_info(self, index):
        self.cluster_info.submit_info(self.write_to_es, index)
        self.indices_manager.submit_info(self.write_to_es, index)
        self.nodes_manager.submit_info(self.write_to_es, index)
