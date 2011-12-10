##############################################################################
#
# Copyright Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import asyncore
import zc.zk
import zope.server.taskthreads
import zope.server.http.wsgihttpserver

def run(wsgi_app, global_conf,
        zookeeper, path, session_timeout=None,
        name=__name__, host='', port=0, threads=1,
        ):
    port = int(port)
    threads = int(threads)

    task_dispatcher = zope.server.taskthreads.ThreadedTaskDispatcher()
    task_dispatcher.setThreadCount(threads)
    server = zope.server.http.wsgihttpserver.WSGIHTTPServer(
        wsgi_app, name, host, port,
        task_dispatcher=task_dispatcher)
    server.ZooKeeper = zc.zk.ZooKeeper(
        zookeeper, session_timeout and int(session_timeout))
    server.ZooKeeper.register_server(
        path, "%s:%s" % server.socket.getsockname())
    try:
        asyncore.loop()
    finally:
        server.ZooKeeper.close()
