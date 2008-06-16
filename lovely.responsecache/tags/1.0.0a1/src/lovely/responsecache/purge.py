##############################################################################
#
# Copyright (c) 2006-2007 Lovely Systems and Contributors.
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
"""

$Id$
"""
__docformat__ = "reStructuredText"

import logging
import threading
import urlparse
import httplib
import transaction

from time import time
from transaction.interfaces import IDataManager

from zope import component, interface
from zope.schema.fieldproperty import FieldProperty

import interfaces


storage = threading.local()
EXPRS_ATTR='varnish_purgeurls'

log = logging.getLogger(__name__)

class PurgeUtil(object):
    """Utilty to purge mutliple caches"""
    interface.implements(interfaces.IPurge)

    def __init__(self, hosts, timeout, retryDelay):
        self.hosts = hosts
        self.timeout = timeout
        self.retryDelay = retryDelay
        self.failedHosts = {}
        self.failLock = threading.Lock()

    def purge(self, expr, escapes='+-'):
        for esc in escapes:
            expr = expr.replace(esc, '\\' + esc)
        if not hasattr(storage, EXPRS_ATTR):
            transaction.get().join(PurgeDataManager(self))
            setattr(storage, EXPRS_ATTR, set([expr]))
        else:
            getattr(storage, EXPRS_ATTR).add(expr)

    def doPurge(self):
        exprs = getattr(storage, EXPRS_ATTR, None)
        if exprs is None:
            return
        for host in self.hosts:
            self.failLock.acquire()
            if host in self.failedHosts.keys():
                if self.failedHosts[host]  + self.retryDelay > time():
                    self.failLock.release()
                    continue
                else:
                    del self.failedHosts[host]
            self.failLock.release()
            def urls(exprs):
                for expr in exprs:
                    url = self._expr2URL(expr)
                    yield urlparse.urlunparse(urlparse.urlparse(host)[:2] + url)
            if not self._purgeURLs(urls(exprs)):
                self.failLock.acquire()
                self.failedHosts[host] = time()
                self.failLock.release()
        self._clearPurge()

    def _clearPurge(self):
        if hasattr(storage, EXPRS_ATTR):
            delattr(storage, EXPRS_ATTR)

    def _expr2URL(self, expr):
        #URL: scheme://netloc/path;parameters?query#fragment
        expr = str(expr)
        if expr.startswith('http://'):
            parts = urlparse.urlparse(expr)
            parts = parts[2:]
        else:
            parts = (expr, '', '', '')
        return parts

    def _purgeURLs(self, urls):
        # this method is set below depending on the availability of pyCurl
        pass

    def ignoreWrite(self, data):
        pass


def _purgePyCurl(self, urls):
    result = True
    url = 'no URL'
    c = pycurl.Curl()
    try:
        c.setopt(c.WRITEFUNCTION, self.ignoreWrite)
        c.setopt(c.CUSTOMREQUEST,'PURGE')
        c.setopt(c.TIMEOUT, self.timeout)
        for url in urls:
            c.setopt(c.URL, url)
            c.perform()
            log.info('purged %r' % url)
    except Exception, e:
        log.error('unable to purge %r, reason: %s' % (url, e))
        result = False
    c.close()
    return result

def _purgeHTTPLIB(self, urls):
    result = True
    try:
        for url in urls:
            parsed = urlparse.urlparse(url)
            host = parsed[1]
            path = parsed[2]
            h = httplib.HTTP(host)
            h.putrequest('PURGE', path)
            h.endheaders()
            errcode, errmsg, headers = h.getreply()
            h.getfile().read()
            h.close()
            log.info('purged %r' % url)
    except Exception, e:
        log.error('unable to purge %r, reason: %s' % (url, e))
        result = False
    return result

try:
    import pycurl
    PurgeUtil._purgeURLs = _purgePyCurl
except ImportError:
    log.warning('Performance alert: pyCurl not found, using httplib!')
    PurgeUtil._purgeURLs = _purgeHTTPLIB


class PurgeDataManager(object):
    """An IDataManager implementation to do purges."""

    interface.implements(IDataManager)

    def __init__(self, util):
        self.util = util

    def _doPurge(self):
        self.util.doPurge()

    def abort(self, txn):
        self.util._clearPurge()

    def tpc_begin(self, txn):
        pass

    def commit(self, txn):
        pass

    def tpc_vote(self, txn):
        pass

    def tpc_finish(self, txn):
        # here we purge
        self.util.doPurge()

    def tpc_abort(self, txn):
        self.util._clearPurge()

    def sortKey(self):
        return "purge_%d" % id(self)

