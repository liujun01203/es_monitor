# !/usr/bin/env python
# coding=utf-8

import json
from oslo_config import cfg

from es_monitor import log as logging
from es_monitor.utils.c2dict import class_to_dict

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

    def __init__(self, line):
        '''
        Constructor
        :param line:
        terms = ["health",  "status", "index_name", "pri", "rep", "docs_count", "docs_deleted", "store_size", "pri_store_size"]
        :return:
        '''
        terms = line.split()
        self.health = terms[0]
        self.status = terms[1]
        self.name = terms[2]
        self.pri_shards = int(terms[3])
        self.rep = int(terms[4])
        self.document_count = int(terms[5])
        self.store_size = terms[7]
        self.search_rate = '0'
        self.indexing_rate = '0'
        self.index_size = '0'
        self.lucene_memory = '0'
        self.field_data_size = '0'

    def update_from_indices_stats(self, resp):
        LOG.debug("resp: %s" % resp)
        self.document_count = resp["total"]["docs"]["count"]

    def submit_info(self, es, index):
        LOG.debug("Enter into submit_info")
        body = json.dumps(class_to_dict(self))  # 字典转换成json
        LOG.debug("body: %s" % body)
        es.index(index=index, doc_type=CONF.dtype_index_info, body=body)
