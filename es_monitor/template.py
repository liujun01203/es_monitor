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
            "_all":{
                "enabled":"false",
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
              "version": {
                  "type": "long"
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
              "status": {
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
                "enabled": "false",
            },
            "date_detection": "false",
            "properties": {
                "total_shards": {
                    "type": "long"
                },
                "ram_percent": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "role": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "documents": {
                    "type": "long"
                },
                "jvm_heap_usage": {
                    "type": "long"
                },
                "type": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "system_load_average": {
                    "type": "long"
                },
                "search_latency": {
                    "type": "long"
                },
                "jvm_mem_heap_used_in_bytes": {
                    "type": "long"
                },
                "segment_count": {
                    "type": "long"
                },
                "load": {
                    "type": "double"
                },
                "mem_total_in_bytes": {
                    "type": "long"
                },
                "host": {
                    "index": "not_analyzed",
                    "type": "string"
                },
                "size_in_bytes": {
                    "type": "long"
                },
                "jvm_memory": {
                    "type": "long"
                },
                "cversion": {
                    "index": "not_analyzed",
                    "type": "string"
                },
                "mem_free_in_bytes": {
                    "type": "long"
                },
                "timestamp": {
                    "format": "epoch_second",
                    "type": "date"
                },
                "disk_free_space": {
                    "type": "long"
                },
                "ip": {
                    "index": "not_analyzed",
                    "type": "string"
                },
                "transport_address": {
                    "index": "not_analyzed",
                    "type": "string"
                },
                "indexing_latency": {
                    "type": "long"
                },
                "jvm_mem_heap_max_in_bytes": {
                    "type": "long"
                },
                "master": {
                    "index": "not_analyzed",
                    "type": "string"
                },
                "heap_percent": {
                    "index": "not_analyzed",
                    "type": "string"
                },
                "shards": {
                    "type": "long"
                },
                "indices": {
                    "type": "long"
                },
                "cpu_utilization": {
                    "type": "long"
                },
                "mem_used_in_bytes": {
                    "type": "long"
                },
                "name": {
                    "index": "not_analyzed",
                    "type": "string"
                },
                "status": {
                    "index": "not_analyzed",
                    "type": "string"
                }
            }
        },
        "index_info": {
            "_all": {
                "enabled": "false",
            },
            "date_detection": "false",
            "properties": {
                "document_count": {
                    "type": "long"
                },
                "field_data_size": {
                    "index": "not_analyzed",
                    "type": "string"
                },
                "index_size": {
                    "index": "not_analyzed",
                    "type": "string"
                },
                "pri_shards": {
                    "type": "long"
                },
                "health": {
                    "index": "not_analyzed",
                    "type": "string"
                },
                "store_size": {
                    "index": "not_analyzed",
                    "type": "string"
                },
                "lucene_memory": {
                    "index": "not_analyzed",
                    "type": "string"
                },
                "search_rate": {
                    "type": "long"
                },
                "name": {
                    "index": "not_analyzed",
                    "type": "string"
                },
                "rep": {
                    "type": "long"
                },
                "indexing_rate": {
                    "type": "long"
                },
                "status": {
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
                "enabled": "false",
            },
            "date_detection": "false",
            "properties": {
                "search_latency": {
                    "type": "long"
                },
                "indexing_latency": {
                    "type": "long"
                },
                "indexing_rate": {
                    "type": "long"
                },
                "search_rate": {
                    "type": "long"
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
