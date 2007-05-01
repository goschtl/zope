##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Zope 3 Monitor Server

$Id$
"""

import os, re, time, traceback

import ZODB.ActivityMonitor
import ZODB.interfaces

import zope.component
import zope.interface
import zope.publisher.browser
import zope.publisher.interfaces.browser
import zope.security.proxy
import zope.traversing.interfaces
import zope.app.appsetup.interfaces
import zope.app.appsetup.product
import zope.app.publication.interfaces

import zc.ngi.adapters

class Server:

    def __init__(self, connection):
        connection = zc.ngi.adapters.Lines(connection)
        self.connection = connection
        connection.setHandler(self)

    def handle_input(self, connection, data):
        args = data.strip().split()
        if not args:
            return
        command = args.pop(0)
        try:
            command = getattr(self, 'command_'+command)
        except AttributeError:
            connection.write('invalid command %r\n' % command)
        else:
            try:
                command(connection, *args)
            except Exception, v:

                traceback.print_exc(100, connection)
                print >> connection, "%s: %s\n" % (v.__class__.__name__, v)

        connection.write(zc.ngi.END_OF_DATA)

    def handle_close(self, connection, reason):
        pass

    def command_help(self, connection):
        print >> connection, "Commands: help z2monitor dbinfo"

    opened_time_search = re.compile('[(](\d+[.]\d*)s[)]').search
    def command_monitor(self, connection, long=100):
        min = float(long)
        db = zope.component.getUtility(ZODB.interfaces.IDatabase)

        result = []
        nconnections = 0
        for data in db.connectionDebugInfo():
            opened = data['opened']
            if not opened:
                continue
            nconnections += 1
            age = float(self.opened_time_search(opened).group(1))
            if age < min:
                continue
            result.append((age, data['info']))

        result.sort()
                
        print >>connection, str(nconnections)
        for status in getStatus():
            print >>connection, status
        for age, info in result:
            print >>connection, age, info.encode('utf-8')

    def command_dbinfo(self, connection, database='', deltat=300):
        if database == '-':
            database = ''
        db = zope.component.getUtility(ZODB.interfaces.IDatabase, database)

        am = db.getActivityMonitor()
        if am is None:
            data = -1, -1, -1
        else:
            now = time.time()
            analysis = am.getActivityAnalysis(now-int(deltat), now, 1)[0]
            data = (analysis['loads'],
                    analysis['stores'],
                    analysis['connections'],
                    )
        print >> connection, data[0], data[1], data[2]


@zope.component.adapter(zope.app.appsetup.interfaces.IDatabaseOpenedEvent)
def initialize(opened_event):
    for name, db in zope.component.getUtilitiesFor(ZODB.interfaces.IDatabase):
        if db.getActivityMonitor() is None:
            db.setActivityMonitor(ZODB.ActivityMonitor.ActivityMonitor())
    
    config = zope.app.appsetup.product.getProductConfiguration(__name__)
    port = int(config['port'])
    import zc.ngi.async
    zc.ngi.async.listener(('', port), Server)

@zope.component.adapter(
    zope.traversing.interfaces.IContainmentRoot,
    zope.app.publication.interfaces.IBeforeTraverseEvent,
    )
def save_request_in_connection_info(object, event):
    object = zope.security.proxy.getObject(object)
    connection = getattr(object, '_p_jar', None)
    if connection is None:
        return
    path = event.request.get('PATH_INFO')
    if path is not None:
        connection.setDebugInfo(path)

class Test(zope.publisher.browser.BrowserPage):
    zope.component.adapts(zope.interface.Interface,
                          zope.publisher.interfaces.browser.IBrowserRequest)

    def __call__(self):
        time.sleep(30)
        return 'OK'

pid = os.getpid()
def getStatus(want=('VmSize', 'VmRSS')):
    for line in open('/proc/%s/status' % pid):
        if (line.split(':')[0] in want):
            yield line.strip()
   
