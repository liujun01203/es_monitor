#!/usr/bin/env python
# coding=utf-8

from oslo_config import cfg
import json

from entity import Entity
from es_monitor import log as logging
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


class ClusterInfo(Entity):

    def __init__(self):
        '''
        Constructor
        '''
        self.name = ''  # cluster name
        self.status = ''  # cluster status
        self.nodes = 0   # number of cluster nodes
        self.indices = 0  # number of cluster index
        self.total_memory = 0  # total memory of cluster
        self.used_memory = 0  # used memory of cluster
        self.total_shards = 0  # shards of cluster
        self.unassigned_shards = 0  # unassigned shards of cluster
        self.documents = 0  # number of documents of cluster
        self.data = 0  # data node number of cluser
        self.uptime = 0  # last time since run
        self.version = 0  # es version
        self.timestamp = None  # timestamp

    def update_from_cat_health(self, resp):
        '''
        resp:
        terms = ["epoch",   "timestamp",   "cluster_name",    "status",   "node_total",
                 "node_data",   "shards",        "pri",                  "relo",      "init",
                 "unassign",    "pending_tasks", "max_task_wait_time",   "active_shards_percent"]
        '''
        LOG.debug("resp: %s" % resp)
        ret = resp.split()
        self.name = ret[2]
        self.status = ret[3]
        self.nodes = int(ret[4])
        self.data = int(ret[5])

    def update_from_cat_count(self, resp):
        '''
        :param resp:
        terms = ["epoch",    "timestamp",     "count"]
        :return:
        '''
        LOG.debug("resp: %s" % resp)
        ret = resp.split()
        self.documents = int(ret[2])

    def update_from_cat_indices(self, resp):
        '''
        :param resp:
        terms = ["health",    "status", "index_name", "pri", "rep", "docs_count", "docs_deleted", "store_size", "pri_store_size"]
        :return:
        '''
        LOG.debug("resp: %s" % resp)
        ret = resp.split('\n')
        self.indices = len(ret)

        for index in ret:
            pass

    def update_from_cluster_stats(self, resp):
        '''
        :param resp:
        :return:
        '''
        LOG.debug("resp: %s" % resp)
        self.indices = resp["indices"]["count"]
        self.total_shards = resp["indices"]["shards"]["total"]

    def update_from_cluster_state(self, resp):
        '''
        :param resp:
        :return:
        '''
        LOG.debug("resp: %s" % resp)

    def update(self, context):
        '''
        update cluster overview info based on context
        :param context:
        :return:
        '''
        LOG.debug("Enter into update")
        if "timestamp" in context:
            self.timestamp = context["timestamp"]

        if "cat_health" in context:
            self.update_from_cat_health(context['cat_health'])

        if "cat_count" in context:
            self.update_from_cat_count(context['cat_count'])

        if "cat_indices" in context:
            self.update_from_cat_indices(context['cat_indices'])

        if "cluster_stats" in context:
            self.update_from_cluster_stats(context['cluster_stats'])

        if "cluster_state" in context:
            self.update_from_cluster_state(context['cluster_state'])

    def submit_info(self, es, index):
        '''
        write cluster overview info to es
        :param es:
        :param index:
        :return:
        '''
        LOG.debug("Enter into submit_info")
        body = json.dumps(class_to_dict(self))
        LOG.info("body: %s" %body)
        es.index(index=index, doc_type=CONF.dtype_cluster_info, body=body)
