#!/usr/bin/env python
# coding=utf-8

import json
from oslo_config import cfg

from es_monitor import log as logging
from es_monitor.index import IndexInfo

LOG = logging.getLogger(__name__)

index_overview_info_opts = [
    cfg.StrOpt(
        'dtype_index_overview_info',
        default='index_overview_info',
        help="doc type for index overview info"
    ),
]

CONF = cfg.CONF
CONF.register_opts(index_overview_info_opts)


class IndicesManager(object):
    """
    pass
    """

    def __init__(self, cluster_manager):
        '''
        Constructor
        '''
        self.indices = set()
        metric_data = {}
        self.last_search_query_total = 0
        self.current_search_query_total = 0
        self.last_search_query_time_in_millis = 0  # size in ms
        self.current_search_query_time_in_millis = 0  # size in ms
        metric_data["search_rate"] = 0.0
        metric_data["search_latency"] = 0.0

        self.last_indexing_total = 0
        self.current_indexing_total = 0
        self.last_indexing_time_in_millis = 0  # size in ms
        self.current_indexing_time_in_millis = 0  # size in ms
        metric_data["indexing_rate"] = 0.0
        metric_data["indexing_latency"] = 0.0

        metric_data["timestamp"] = None
        self.metric_data = metric_data
        self.check_interval = 0  # in seconds
        self.cluster_manager = cluster_manager

    def set_check_interval(self, check_interval):
        self.check_interval = check_interval

    def set_timestamp(self, timestamp):
        metric_data = self.metric_data
        metric_data["timestamp"] = timestamp

    def update(self, context):
        '''
        :param context:
        :return:
        '''
        if "timestamp" in context:
            self.set_timestamp(context["timestamp"])

        if "cat_indices" in context:
            self.update_from_cat_indices(context["cat_indices"])

        if "cluster_stats" in context:
            self.update_from_cluster_stats(context["cluster_stats"])

        if "cluster_state" in context:
            self.update_from_cluster_state(context["cluster_state"])

        if "cluster_health" in context:
            self.update_from_cluster_health(context["cluster_health"])

        if "indices_stats" in context:
            self.update_from_indices_stats(context["indices_stats"])

    def update_from_cluster_health(self, resp):
        LOG.debug("resp: %s" % resp)
        indices = resp["indices"]
        for k, v in indices.iteritems():
            index_info = self.get_index_info(k)
            index_info.update_from_indices_health(v)

    def update_from_cat_indices(self, resp):
        '''
        :param resp:
        yellow open  .marvel-es-2016.10.25 1 1 71398 48 18.8mb 18.8mb
        yellow open  .kibana               1 1     4  0 28.9kb 28.9kb
        yellow open  .monitor-2016-10-26   1 1   539  0  209kb  209kb
        yellow open  .marvel-es-data       1 1     1  0  7.2kb  7.2kb
               close .marvel-es-2016.10.24
        yellow open  .marvel-es-2016.10.26 1 1 23218 48  6.5mb  6.5mb
        :return:
        '''
        LOG.debug("resp: %s" % resp)
        lines = resp.split('\n')
        for line in lines:
            line.strip()
            if line:
                index = IndexInfo(line, self)
                self.indices.add(index)

    def update_from_cluster_stats(self, resp):
        LOG.debug("resp: %s" % resp)
        pass

    def update_from_cluster_state(self, resp):
        LOG.debug("resp: %s" % resp)
        pass

    def update_overview_info_from_indices_stats(self, resp):
        LOG.debug("resp: %s" % resp)
        metric_data = self.metric_data
        resp_total = resp["total"]

        self.last_search_query_total = self.current_search_query_total
        self.current_search_query_total = resp_total["search"]["query_total"]
        self.last_search_query_time_in_millis = self.current_search_query_time_in_millis
        self.current_search_query_time_in_millis = resp_total["search"]["query_time_in_millis"]
        delta_time_in_millis = self.current_search_query_time_in_millis - self.last_search_query_time_in_millis
        delta_request = self.current_search_query_total - self.last_search_query_total

        if self.last_search_query_total != 0:
            metric_data["search_rate"] = delta_request * 1.0 / self.check_interval
            if delta_request != 0:
                metric_data["search_latency"] = delta_time_in_millis * 1.0 / delta_request

        self.last_indexing_total = self.current_indexing_total
        self.current_indexing_total = resp_total["indexing"]["index_total"]
        self.last_indexing_time_in_millis = self.current_indexing_time_in_millis
        self.current_indexing_time_in_millis = resp_total["indexing"]["index_time_in_millis"]
        delta_time_in_millis = self.current_indexing_time_in_millis - self.last_indexing_time_in_millis
        delta_request = self.current_indexing_total - self.last_indexing_total

        if self.last_indexing_total != 0:
            metric_data["indexing_rate"] = delta_request * 1.0 / self.check_interval
            if delta_request != 0:
                metric_data["indexing_latency"] = delta_time_in_millis * 1.0 / delta_request
        return

    def update_from_indices_stats(self, resp):
        '''
        :param resp:

        {
            "_shards": {},
            "_all": {
                "primaries": {
                    "docs": {},
                    "store": {},
                    "indexing": {
                        "index_total": 241642,
                        "index_time_in_millis": 43422,
                        "index_current": 2,
                        "delete_total": 0,
                        "delete_time_in_millis": 0,
                        "delete_current": 0,
                        "noop_update_total": 0,
                        "is_throttled": false,
                        "throttle_time_in_millis": 0
                    },
                    "get": {},
                    "search": {
                        "open_contexts": 0,
                        "query_total": 269119,
                        "query_time_in_millis": 124292,
                        "query_current": 0,
                        "fetch_total": 133771,
                        "fetch_time_in_millis": 1940796,
                        "fetch_current": 0,
                        "scroll_total": 0,
                        "scroll_time_in_millis": 0,
                        "scroll_current": 0
                    },
                    "merges": {},
                    "refresh": {},
                    "flush": {},
                    "warmer": {},
                    "query_cache": {},
                    "fielddata": {},
                    "percolate": {},
                    "completion": {
                        "size_in_bytes": 0
                    },
                    "segments": {},
                    "translog": {},
                    "suggest": {},
                    "request_cache": {},
                    "recovery": {}
                },
                "total": {
                    "docs": {},
                    "store": {},
                    "indexing": {},
                    "get": {},
                    "search": {},
                    "merges": {},
                    "refresh": {},
                    "flush": {},
                    "warmer": {},
                    "query_cache": {},
                    "fielddata": {},
                    "percolate": {},
                    "completion": {},
                    "segments": {},
                    "translog": {},
                    "suggest": {},
                    "request_cache": {},
                    "recovery": {}
                }
            },
            "indices": {}
        }
        :return:
        '''
        LOG.debug("resp: %s" % resp)
        indices_overview = resp["_all"]
        indices = resp["indices"]
        self.update_overview_info_from_indices_stats(indices_overview)

        for k, v in indices.iteritems():
            index_info = self.get_index_info(k)
            index_info.update_from_indices_stats(v)

    def get_index_info(self, name):
        for index in self.indices:
            if name == index.metric_data["name"]:
                return index

    def submit_info(self, es, index):
        LOG.debug("Enter into submit_info")
        body = json.dumps(self.metric_data)
        LOG.debug("body: %s" % body)
        es.index(index=index, doc_type=CONF.dtype_index_overview_info, body=body)

        for idex in self.indices:  # note idex not index
            idex.set_timestamp(self.metric_data["timestamp"])
            idex.submit_info(es, index)
