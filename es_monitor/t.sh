curl -XPUT localhost:9200/.marvel*/_settings -d '{  "index": {    "search.slowlog.level": "trace",    "search.slowlog.threshold.query.trace": "0ms",   "search.slowlog.threshold.fetch.trace": "0ms" }}'