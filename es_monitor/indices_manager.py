#!/usr/bin/env python
# coding=utf-8

import json
from oslo_config import cfg

from es_monitor.entity import Entity
from es_monitor import log as logging
from es_monitor.index import IndexInfo

LOG = logging.getLogger(__name__)

index_overview_info_opts = [
        cfg.StrOpt(
            'dtype_index_overview_info',
            default='index_overview_info',
            help="doc type for index overview info"),
        ]

CONF = cfg.CONF
CONF.register_opts(index_overview_info_opts)


class IndicesManager(Entity):
    """
    pass
    """

    def __init__(self):
        '''
        Constructor
        '''
        self.indices = []
        dict_data = {}
        dict_data["search_rate"] = 0
        dict_data["search_latency"] = 0
        dict_data["indexing_rate"] = 0
        dict_data["indexing_latency"] = 0
        self.dict_data = dict_data

    def update(self, context):
        '''
        :param context:
        :return:
        '''
        if "timestamp" in context:
            self.dict_data["timestamp"] = context["timestamp"]

        if "cat_indices" in context:
            self.update_from_cat_indices(context["cat_indices"])

        if "cluster_stats" in context:
            self.update_from_cluster_stats(context["cluster_stats"])

        if "cluster_state" in context:
            self.update_from_cluster_state(context["cluster_state"])

        if "indices_stats" in context:
            self.update_from_indices_stats(context["indices_stats"])

    def update_from_cat_indices(self, resp):
        LOG.debug("resp: %s" % resp)
        lines = resp.split('\n')
        for line in lines:
            line.strip()
            if line:
                index = IndexInfo(line)
                index.timestamp = self.dict_data["timestamp"]
                self.indices.append(index)

    def update_from_cluster_stats(self, resp):
        LOG.debug("resp: %s" % resp)
        pass

    def update_from_cluster_state(self, resp):
        LOG.debug("resp: %s" % resp)
        pass

    def update_overview_info(self, resp):
        LOG.debug("resp: %s" % resp)
        return

    def update_from_indices_stats(self, resp):
        LOG.debug("resp: %s" % resp)
        indices_overview = resp["_all"]
        indices = resp["indices"]
        self.update_overview_info(indices_overview)

        for k, v in indices.iteritems():
            index_info = self.get_index_info(k)
            index_info.update_from_indices_stats(v)

    def get_index_info(self, name):
        for index in self.indices:
            if name == index.name:
                return index

    def submit_info(self, es, index):
        LOG.debug("Enter into submit_info")
        body = json.dumps(self.dict_data)
        LOG.debug("body: %s" % body)
        es.index(index=index, doc_type=CONF.dtype_index_overview_info, body=body)
        for idex in self.indices:
            idex.submit_info(es, index)
