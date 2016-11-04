# !/usr/bin/env python
# coding=utf-8

import json
from oslo_config import cfg

from es_monitor import log as logging

LOG = logging.getLogger(__name__)

index_info_opts = [
    cfg.StrOpt(
        'dtype_index_info',
        default='index_info',
        help="doc type for index info"
    ),
]

CONF = cfg.CONF
CONF.register_opts(index_info_opts)


class IndexInfo(object):

    def __init__(self, line, indices_manager):
        '''
        Constructor
        :param line:
        #health status index                 pri rep docs.count docs.deleted store.size pri.store.size
               close  .marvel-es-2016.10.24
        yellow open   .marvel-es-2016.10.26   1   1      23318           40      6.4mb          6.4mb
        :return:
        '''
        self.manager = indices_manager
        metric_data = {}
        metric_data["search_rate"] = 0.0
        self.last_search_query_total = 0
        self.current_search_query_total = 0

        metric_data["indexing_rate"] = 0.0
        self.last_indexing_total = 0
        self.current_indexing_total = 0

        metric_data["index_size"] = 0  # size in bytes
        metric_data["lucene_memory"] = 0  # size in bytes
        metric_data["field_data_size"] = 0

        metric_data["health"] = ''
        metric_data["document_count"] = 0
        metric_data["data"] = 0
        metric_data["total_shards"] = 0
        metric_data["unassigned_shards"] = 0
        metric_data["name"] = ''
        metric_data["timestamp"] = None
        self.metric_data = metric_data

        self.update_from_cat_indices(line)

    def __eq__(self, other):
        try:
            return self.metric_data["name"] == other.metric_data["name"]
        except:
            return False

    def __hash__(self):
        return hash(self.metric_data["name"])

    def update_from_cat_indices(self, line):
        metric_data = self.metric_data
        terms = line.split()
        if len(terms) == 9 and terms[1] == 'open':
            metric_data["status"] = terms[1]
            metric_data["health"] = terms[0]
            metric_data["document_count"] = int(terms[5])
            metric_data["name"] = terms[2]
        elif terms[0] == 'close':
            metric_data["status"] = terms[0]
            metric_data["health"] = 'unknown'
            metric_data["name"] = terms[1]

    def reset_metrics(self):
        metric_data = self.metric_data
        metric_data["search_rate"] = 0.0
        metric_data["indexing_rate"] = 0.0
        metric_data["index_size"] = 0
        metric_data["lucene_memory"] = 0
        metric_data["field_data_size"] = 0
        metric_data["status"] = "unknown"
        metric_data["health"] = ''
        metric_data["document_count"] = 0
        metric_data["data"] = 0
        metric_data["total_shards"] = 0
        metric_data["unassigned_shards"] = 0
        metric_data["timestamp"] = None

    def set_timestamp(self, timestamp):
        metric_data = self.metric_data
        metric_data["timestamp"] = timestamp

    def update_from_indices_stats(self, resp):
        '''
        :param resp:
        ".kibana": {
            "primaries": {
                "docs": {
                    "count": 4,
                    "deleted": 0
                 },
                "store": {
                    "size_in_bytes": 29611,
                    "throttle_time_in_millis": 0
                },
                "indexing": {
                    "index_total": 11,
                    "index_time_in_millis": 33,
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
                "query_total": 9797,
                "query_time_in_millis": 594,
                "query_current": 0,
                "fetch_total": 9520,
                "fetch_time_in_millis": 431,
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
                "percolate": { },
                "completion": {},
                "segments": {},
                "translog": {},
                "suggest": {},
                "request_cache": {},
                "recovery": {}
            },
            "total": {
                "docs": {},
                "store": {
                "size_in_bytes": 29611,
                "throttle_time_in_millis": 0
                },
                "indexing": {
                "index_total": 11,
                "index_time_in_millis": 33,
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
                "query_total": 9797,
                "query_time_in_millis": 594,
                "query_current": 0,
                "fetch_total": 9520,
                "fetch_time_in_millis": 431,
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
                "fielddata": {
                "memory_size_in_bytes": 0,
                "evictions": 0
                },
                "percolate": {},
                "completion": {},
                "segments": {
                "count": 3,
                "memory_in_bytes": 12100,
                "terms_memory_in_bytes": 10768,
                "stored_fields_memory_in_bytes": 936,
                "term_vectors_memory_in_bytes": 0,
                "norms_memory_in_bytes": 120,
                "doc_values_memory_in_bytes": 276,
                "index_writer_memory_in_bytes": 0,
                "index_writer_max_memory_in_bytes": 512000,
                "version_map_memory_in_bytes": 0,
                "fixed_bit_set_memory_in_bytes": 0
                },
                "translog": {},
                "suggest": {},
                "request_cache": {},
                "recovery": {}
            }
        },
        :return:
        '''
        LOG.debug("resp: %s" % resp)
        metric_data = self.metric_data
        resp_total = resp["total"]
        metric_data["document_count"] = resp_total["docs"]["count"]
        metric_data["data"] = resp_total["store"]["size_in_bytes"]
        metric_data["field_data_size"] = resp_total["fielddata"]["memory_size_in_bytes"]
        self.last_indexing_total = self.current_indexing_total
        self.current_indexing_total = resp_total["indexing"]["index_total"]
        if self.last_indexing_total != 0:
            metric_data["indexing_rate"] = (self.current_indexing_total - self.last_indexing_total)/self.manager.check_interval
        self.last_search_query_total = self.current_search_query_total
        self.current_search_query_total = resp_total["search"]["query_total"]
        if self.last_search_query_total != 0:
            metric_data["search_rate"] = (self.current_search_query_total - self.last_search_query_total)/self.manager.check_interval

        metric_data["index_size"] = resp_total["store"]["size_in_bytes"]  # size in bytes
        metric_data["lucene_memory"] = resp_total["segments"]["memory_in_bytes"]  # size in bytes

    def update_from_indices_health(self, resp):
        '''
        :param resp:
        ".kibana" : {
            "status" : "yellow",
            "number_of_shards" : 1,
            "number_of_replicas" : 1,
            "active_primary_shards" : 1,
            "active_shards" : 1,
            "relocating_shards" : 0,
            "initializing_shards" : 0,
            "unassigned_shards" : 1,
            "shards" : {
                "0" : {
                "status" : "yellow",
                "primary_active" : true,
                "active_shards" : 1,
                "relocating_shards" : 0,
                "initializing_shards" : 0,
                "unassigned_shards" : 1
                }
            }
        },
        :return:
        '''
        LOG.debug("resp: %s" % resp)
        metric_data = self.metric_data
        metric_data["total_shards"] = resp["number_of_shards"]
        metric_data["unassigned_shards"] = resp["unassigned_shards"]

    def submit_info(self, es, index):
        LOG.debug("Enter into submit_info")
        body = json.dumps(self.metric_data)
        LOG.debug("body: %s" % body)
        es.index(index=index, doc_type=CONF.dtype_index_info, body=body)
        self.reset_metrics()
