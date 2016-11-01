#!/usr/bin/env python
# coding=utf-8

default_template = {
    "order": 0,
    "template": ".monitor-*",
    "settings": {
        "index": {
            "mapper": {
                "dynamic": "false"
            },
            "number_of_shards": "1",
            "number_of_replicas": "1"
        }
    },
    "mappings": {
        "cluster_info": {
            "_all": {
                "enabled": "false"
            },
            "date_detection": "false",
            "properties": {
                "total_shards": {
                    "type": "long"
                },
                "data": {
                    "type": "long"
                },
                "unassigned_shards": {
                    "type": "long"
                },
                "documents": {
                    "type": "long"
                },
                "used_memory": {
                    "type": "long"
                },
                "es_version": {
                    "type": "string"
                },
                "uptime": {
                    "type": "long"
                },
                "indices": {
                    "type": "long"
                },
                "nodes": {
                    "type": "long"
                },
                "total_memory": {
                    "type": "long"
                },
                "name": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "health": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "timestamp": {
                    "format": "epoch_second",
                    "type": "date"
                }
            }
        },
        "node_info": {
            "_all": {
                "enabled": "false"
            },
            "date_detection": "false",
            "properties": {
                "name": {
                    "index": "not_analyzed",
                    "type": "string"
                },
                "host": {
                    "index": "not_analyzed",
                    "type": "string"
                },
                "ip": {
                    "index": "not_analyzed",
                    "type": "string"
                },
                "documents": {
                    "type": "long"
                },
                "data": {
                    "type": "long"
                },
                "disk_free_space": {
                    "type": "long"
                },
                "indices": {
                    "type": "long"
                },
                "total_shards": {
                    "type": "long"
                },
                "search_latency": {
                    "type": "double"
                },
                "indexing_latency": {
                    "type": "double"
                },
                "jvm_heap_usage": {
                    "type": "long"
                },
                "cpu_utilization": {
                    "type": "double"
                },
                "system_load_average": {
                    "type": "double"
                },
                "segment_count": {
                    "type": "long"
                },
                "timestamp": {
                    "format": "epoch_second",
                    "type": "date"
                }
            }
        },
        "index_info": {
            "_all": {
                "enabled": "false"
            },
            "date_detection": "false",
            "properties": {
                "search_rate": {
                    "type": "double"
                },
                "indexing_rate": {
                    "type": "double"
                },
                "index_size": {
                    "index": "not_analyzed",
                    "type": "long"
                },
                "lucene_memory": {
                    "type": "long"
                },
                "document_count": {
                    "type": "long"
                },
                "field_data_size": {
                    "index": "not_analyzed",
                    "type": "long"
                },
                "status": {
                    "index": "not_analyzed",
                    "type": "string"
                },
                "data": {
                    "type": "long"
                },
                "total_shards": {
                    "type": "long"
                },
                "unassigned_shards": {
                    "type": "long"
                },
                "name": {
                    "index": "not_analyzed",
                    "type": "string"
                },
                "health": {
                    "index": "not_analyzed",
                    "type": "string"
                },
                "timestamp": {
                    "format": "epoch_second",
                    "type": "date"
                }
            }
        },
        "index_overview_info": {
            "_all": {
                "enabled": "false"
            },
            "date_detection": "false",
            "properties": {
                "search_latency": {
                    "type": "double"
                },
                "indexing_latency": {
                    "type": "double"
                },
                "indexing_rate": {
                    "type": "double"
                },
                "search_rate": {
                    "type": "double"
                },
                "timestamp": {
                    "format": "epoch_second",
                    "type": "date"
                }
            }
        }
    },
    "aliases": {}
}
