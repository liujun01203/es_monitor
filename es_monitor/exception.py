#!/usr/bin/env python
# coding=utf-8


class EsMonitorException(Exception):

    msg_fmt = "An unknown exception occurred."

    def __init__(self, message=None, **kwargs):
        if not message:
            message = self.msg_fmt % kwargs
        super(EsMonitorException, self).__init__(message)


class CatHealthException(EsMonitorException):
    msg_fmt = "Cat Health Response Error"


class CatCountException(EsMonitorException):
    msg_fmt = "Cat Count Response Error"


class CatIndicesException (EsMonitorException):
    msg_fmt = "Cat Indices Response Error"


class CatNodesException(EsMonitorException):
    msg_fmt = "Cat Nodes Response Error"


class ClusterStatsException(EsMonitorException):
    msg_fmt = "Cluster Stats Response Error"


class ClusterStateException(EsMonitorException):
    msg_fmt = "Cluster State Response Error"


class IndicesStatsException(EsMonitorException):
    msg_fmt = "Indices Stats Response Error"


class NodesInfoException(EsMonitorException):
    msg_fmt = "Nodes Info Response Error"


class NodesStatsException(EsMonitorException):
    msg_fmt = "Nodes Stats Response Error"
