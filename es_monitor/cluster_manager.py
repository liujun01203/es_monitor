#!/usr/bin/env python
# coding=utf-8

from elasticsearch import Elasticsearch
import time
import json
from oslo_config import cfg

from es_monitor.nodes_manager import NodesManager
from es_monitor.indices_manager import IndicesManager
from es_monitor.cluster import ClusterInfo
from es_monitor import log as logging
from es_monitor import exception
from es_monitor.utils.c2dict import class_to_dict

LOG = logging.getLogger(__name__)


cluster_info_opts = [
    cfg.StrOpt(
        'dtype_cluster_info',
        default='cluster_info',
        help="doc type for cluster info"),
]

CONF = cfg.CONF
CONF.register_opts(cluster_info_opts)


class ClusterManager(object):
    """
    Cluster Manager
    """

    def __init__(self, hosts=None, transport_class=None, **kwargs):
        '''
        Constructor
        :param hosts:
        :param transport_class:
        :param kwargs:
        '''
        metric_data = {}
        metric_data["name"] = ''  # cluster name
        metric_data["health"] = ''  # cluster health
        metric_data["nodes"] = 0   # number of cluster nodes
        metric_data["indices"] = 0  # number of cluster index
        metric_data["total_memory"] = 0  # total memory of cluster for jvm (byte)
        metric_data["used_memory"] = 0  # used memory of cluster for jvm (byte)
        metric_data["total_shards"] = 0  # active shards of cluster
        metric_data["unassigned_shards"] = 0  # unassigned shards of cluster
        metric_data["documents"] = 0  # number of documents of cluster
        metric_data["data"] = 0  # data capacity in byte
        metric_data["uptime"] = 0  # elapsed time since run
        metric_data["es_version"] = 0  # es versions
        metric_data["timestamp"] = None  # timestamp
        self.metric_data = metric_data

        self.es = Elasticsearch(hosts=hosts)
        self.indices = self.es.indices
        self.cluster = self.es.cluster
        self.cat = self.es.cat
        self.nodes = self.es.nodes
        self.check_interval = 0
        self.indices_manager = IndicesManager(self)
        self.nodes_manager = NodesManager(self)
        self.write_to_es = None

    def setup_write_to_es(self, hosts=None, transport_class=None, **kwargs):
        self.write_to_es = Elasticsearch(hosts=hosts)

    def set_check_interval(self, check_interval):
        self.check_interval = check_interval
        self.indices_manager.set_check_interval(check_interval)
        self.nodes_manager.set_check_interval(check_interval)

    def set_timestamp(self):
        metric_data = self.metric_data
        timestamp = int(time.time())
        metric_data["timestamp"] = timestamp
        self.indices_manager.set_timestamp(timestamp)
        self.nodes_manager.set_timestamp(timestamp)

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
        self.set_timestamp()

        try:
            context["cat_health"] = self.cat.health()
        except:
            raise exception.CatHealthException()

        try:
            context["cat_count"] = self.cat.count()
        except:
            raise exception.CatCountException()

        try:
            cat_indices_format = "health,status,index,pri,rep,docs.count,docs.deleted,store.size,pri.store.size"
            context["cat_indices"] = self.cat.indices(h=cat_indices_format)
        except:
            raise exception.CatIndicesException()

        try:
            cat_nodes_format = "name,ip,load,segments.count,heap.percent,host"
            context["cat_nodes"] = self.cat.nodes(h=cat_nodes_format)
        except:
            raise exception.CatNodesException()

        try:
            cat_shards_format = "state,node,shard,prirep,docs,index"
            context["cat_shards"] = self.cat.shards(h=cat_shards_format)
        except:
            raise exception.CatShardsException()

        try:
            context["cluster_stats"] = self.cluster.stats()
        except:
            raise exception.ClusterStatsException()

        try:
            context["cluster_state"] = self.cluster.state()
        except:
            raise exception.ClusterStateException()

        try:
            context["cluster_health"] = self.cluster.health(level='indices')
        except:
            raise exception.ClusterHealthException()

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
        if "cat_health" in self.context:
            self.update_from_cat_health(self.context['cat_health'])

        if "cat_count" in self.context:
            self.update_from_cat_count(self.context['cat_count'])

        if "cat_indices" in self.context:
            self.update_from_cat_indices(self.context['cat_indices'])

        if "cat_shards" in self.context:
            self.update_from_cat_shards(self.context['cat_shards'])

        if "cluster_stats" in self.context:
            self.update_from_cluster_stats(self.context['cluster_stats'])

        if "cluster_state" in self.context:
            self.update_from_cluster_state(self.context['cluster_state'])

        if "cluster_health" in self.context:
            self.update_from_cluster_health(self.context['cluster_health'])

    def update_from_cat_health(self, resp):
        '''
        resp:
        terms = ["epoch",   "timestamp",   "cluster_name",    "health",   "node_total",
                 "node_data",   "shards",        "pri",                  "relo",      "init",
                 "unassign",    "pending_tasks", "max_task_wait_time",   "active_shards_percent"]
        '''
        LOG.debug("resp: %s" % resp)
        metric_data = self.metric_data
        ret = resp.split()
        metric_data["name"] = ret[2]
        metric_data["health"] = ret[3]
        metric_data["nodes"] = int(ret[4])

    def update_from_cat_count(self, resp):
        '''
        :param resp:
        terms = ["epoch",    "timestamp",     "count"]
        :return:
        '''
        LOG.debug("resp: %s" % resp)
        metric_data = self.metric_data
        ret = resp.split()
        metric_data["documents"] = int(ret[2])

    def update_from_cat_indices(self, resp):
        '''
        :param resp:
        terms = ["health",    "health", "index_name", "pri", "rep", "docs_count", "docs_deleted", "store_size", "pri_store_size"]
        :return:
        '''
        LOG.debug("resp: %s" % resp)
        metric_data = self.metric_data
        ret = resp.split('\n')
        metric_data["indices"] = len(ret)

        for index in ret:
            pass

    def update_from_cluster_stats(self, resp):
        '''
        :param resp:
        :return:
        '''
        LOG.debug("resp: %s" % resp)
        metric_data = self.metric_data
        metric_data["indices"] = resp["indices"]["count"]
        metric_data["total_shards"] = resp["indices"]["shards"]["total"]
        metric_data["data"] = resp["indices"]["store"]["size_in_bytes"]
        metric_data["es_version"] = resp["nodes"]["versions"]
        metric_data["uptime"] = resp["nodes"]["jvm"]["max_uptime_in_millis"]
        metric_data["total_memory"] = resp["nodes"]["jvm"]["mem"]["heap_max_in_bytes"]
        metric_data["used_memory"] = resp["nodes"]["jvm"]["mem"]["heap_used_in_bytes"]

    def update_from_cluster_state(self, resp):
        '''
        :param resp:
        :return:
        '''
        LOG.debug("resp: %s" % resp)
        pass

    def update_from_cluster_health(self, resp):
        '''
        :param resp:
        {
        "cluster_name": "elasticsearch",
        "status": "yellow",
        "timed_out": false,
        "number_of_nodes": 1,
        "number_of_data_nodes": 1,
        "active_primary_shards": 3,
        "active_shards": 3,
        "relocating_shards": 0,
        "initializing_shards": 0,
        "unassigned_shards": 3,
        "delayed_unassigned_shards": 0,
        "number_of_pending_tasks": 0,
        "number_of_in_flight_fetch": 0,
        "task_max_waiting_in_queue_millis": 0,
        "active_shards_percent_as_number": 50
        }
        :return:
        '''
        LOG.debug("resp: %s" % resp)
        metric_data = self.metric_data
        metric_data["unassigned_shards"] = resp["unassigned_shards"]

    def update_from_cat_shards(self, resp):
        '''
        :param resp:
        .kibana               0 p STARTED        2 15.4kb 127.0.0.1 Fever Pitch
        .kibana               0 r UNASSIGNED
        .marvel-es-2016.10.24 0 p STARTED    35026  8.7mb 127.0.0.1 Fever Pitch
        .marvel-es-2016.10.24 0 r UNASSIGNED
        .marvel-es-2016.10.26 0 p STARTED    10418  2.8mb 127.0.0.1 Fever Pitch
        .marvel-es-2016.10.26 0 r UNASSIGNED
        .marvel-es-2016.10.25 0 p STARTED    71398 18.8mb 127.0.0.1 Fever Pitch
        .marvel-es-2016.10.25 0 r UNASSIGNED
        .marvel-es-data       0 p STARTED        1  7.2kb 127.0.0.1 Fever Pitch
        .marvel-es-data       0 r UNASSIGNED
        :return:
        '''
        pass

    def indices_info_update(self):
        LOG.debug("Enter into indices_info_update")
        self.indices_manager.update(self.context)

    def nodes_info_update(self):
        LOG.debug("Enter into nodes_info_update")
        self.nodes_manager.update(self.context)

    def submit_info(self, index):
        '''
        write cluster overview info to es
        :param es:
        :param index:
        :return:
        '''
        LOG.debug("Enter into submit_info")
        body = json.dumps(self.metric_data)
        LOG.debug("body: %s" % body)
        self.write_to_es.index(index=index, doc_type=CONF.dtype_cluster_info, body=body)
        self.indices_manager.submit_info(self.write_to_es, index)
        self.nodes_manager.submit_info(self.write_to_es, index)
