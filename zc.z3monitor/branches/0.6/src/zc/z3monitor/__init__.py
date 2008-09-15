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
"""

import errno, logging, os, re, time, traceback, socket

import ZODB.ActivityMonitor
import ZODB.interfaces

import zope.component
import zope.component.interfaces
import zope.interface
import zope.publisher.browser
import zope.publisher.interfaces.browser
import zope.security.proxy
import zope.traversing.interfaces
import zope.app.appsetup.interfaces
import zope.app.appsetup.product
import zope.app.publication.interfaces

import zc.ngi.adapters

INTERACTIVE_MARKER = object()
QUIT_MARKER = object()

class Server:

    def __init__(self, connection):
        connection = zc.ngi.adapters.Lines(connection)
        self.connection = connection
        connection.setHandler(self)
        self.mode = QUIT_MARKER

    def handle_input(self, connection, data):
        args = data.strip().split()
        if not args:
            return
        command_name = args.pop(0)
        command = zope.component.queryUtility(
            zc.z3monitor.interfaces.IZ3MonitorPlugin,
            command_name)
        if command is None:
            connection.write(
                'Invalid command %r\nTry "help".\n' % command_name)
        else:
            try:
                res = command(connection, *args)
            except Exception, v:
                traceback.print_exc(100, connection)
                print >> connection, "%s: %s\n" % (v.__class__.__name__, v)
            if res is INTERACTIVE_MARKER:
                self.mode = res
            elif res is QUIT_MARKER:
                self.mode = res

        if self.mode is QUIT_MARKER:
            connection.write(zc.ngi.END_OF_DATA)


def interactive(connection):
    """Turn on monitor's interactive mode
    
    Normally, the monitor releases the connection after a single command.
    By entering the interactive mode, the monitor will not end the connection
    until you enter the "quit" command.
    """
    connection.write('Interactive mode on.  Use "quit" To exit.\n')
    return INTERACTIVE_MARKER

def quit(connection):
    """Quit the monitor
    
    This is only really useful in interactive mode (see the "interactive"
    command).
    """
    connection.write('Goodbye.\n')
    return QUIT_MARKER

def help(connection, command_name=None):
    """Get help about server commands

    By default, a list of commands and summaries is printed.  Provide
    a command name to get detailed documentation for a command.
    """
    if command_name is None:
        connection.write(str(
            "Supported commands:\n  "
            + '\n  '.join(sorted(
                "%s -- %s" % (name, (u.__doc__ or '?').split('\n', 1)[0])
                for (name, u) in
                zope.component.getUtilitiesFor(
                    zc.z3monitor.interfaces.IZ3MonitorPlugin)))
            + '\n'))
    else:
        command = zope.component.getUtility(
            zc.z3monitor.interfaces.IZ3MonitorPlugin,
            command_name)
        connection.write("Help for %s:\n\n%s\n"
                         % (command_name, command.__doc__)
                         )

opened_time_search = re.compile('[(](\d+[.]\d*)s[)]').search

def monitor(connection, long=100, database=''):
    # this order of arguments is often inconvenient, but supports legacy usage
    # in which ``database`` was not an option.
    """Get general process info

    The minimal output has:

    - The number of open database connections to the main database, which
      is the database registered without a name.
    - The virtual memory size, and
    - The resident memory size.

    If there are old database connections, they will be listed.  By
    default, connections are considered old if they are greater than 100
    seconds old. You can pass a minimum old connection age in seconds.
    If you pass a value of 0, you'll see all connections.

    If you pass a name after the integer, this is used as the database name.
    The database name defaults to the empty string ('').
    """

    min = float(long)
    db = zope.component.getUtility(ZODB.interfaces.IDatabase, database)

    result = []
    nconnections = 0
    for data in db.connectionDebugInfo():
        opened = data['opened']
        if not opened:
            continue
        nconnections += 1
        match = opened_time_search(opened)
        # XXX the code originally didn't make sure a there was really a
        # match; which caused exceptions in some (unknown) circumstances
        # that we weren't able to reproduce; this hack keeps that from
        # happening
        if not match:
            continue
        age = float(match.group(1))
        if age < min:
            continue
        result.append((age, data['info']))

    result.sort()

    print >>connection, str(nconnections)
    for status in getStatus():
        print >>connection, status
    for age, info in result:
        print >>connection, age, info.encode('utf-8')

def dbinfo(connection, database='', deltat=300):
    """Get database statistics

    By default statistics are returned for the main database.  The
    statistics are returned as a single line consisting of the:

    - number of database loads

    - number of database stores

    - number of connections in the last five minutes

    - number of objects in the object caches (combined)

    - number of non-ghost objects in the object caches (combined)

    You can pass a database name, where "-" is an alias for the main database.

    By default, the statistics are for a sampling interval of 5
    minutes.  You can request another sampling interval, up to an
    hour, by passing a sampling interval in seconds after the database name.    
    """
    
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

    ng = s = 0
    for detail in db.cacheDetailSize():
        ng += detail['ngsize']
        s += detail['size']

    print >> connection, data[0], data[1], data[2], s, ng

def zeocache(connection, database=''):
    """Get ZEO client cache statistics

    The command returns data in a single line:

    - the number of records added to the cache,

    - the number of bytes added to the cache,

    - the number of records evicted from the cache,

    - the number of bytes evicted from the cache,

    - the number of cache accesses.

    By default, data for the main database are returned.  To return
    information for another database, pass the database name.
    """
    
    db = zope.component.getUtility(ZODB.interfaces.IDatabase, database)
    print >> connection, ' '.join(map(str, db._storage._cache.fc.getStats()))

def zeostatus(connection, database=''):
    """Get ZEO client status information

    The command returns True if the client is connected and False otherwise.

    By default, data for the main database are returned.  To return
    information for another database, pass the database name.
    """
    
    db = zope.component.getUtility(ZODB.interfaces.IDatabase, database)
    print >> connection, db._storage.is_connected()

@zope.component.adapter(zope.app.appsetup.interfaces.IDatabaseOpenedEvent)
def initialize(opened_event):
    config = zope.app.appsetup.product.getProductConfiguration(__name__)
    if config is None:
        return

    for name, db in zope.component.getUtilitiesFor(ZODB.interfaces.IDatabase):
        if db.getActivityMonitor() is None:
            db.setActivityMonitor(ZODB.ActivityMonitor.ActivityMonitor())

    port = int(config['port'])
    import zc.ngi.async
    try:
        zc.ngi.async.listener(('', port), Server)
    except socket.error, e:
        if e.args[0] == errno.EADDRINUSE:
            # this might be a zopectl debug.  Don't kill the process just
            # because somebody else has our port.
            logging.warning(
                'unable to start z3monitor server because port %d is in use.',
                port)
        else:
            raise
        

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
    if not os.path.exists('/proc/%s/status' % pid):
        return
    for line in open('/proc/%s/status' % pid):
        if (line.split(':')[0] in want):
            yield line.strip()

