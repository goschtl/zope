##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Error reporting service

This is a port of the Zope 2 error reporting object

$Id$
"""
__docformat__ = 'restructuredtext'

import time
import logging
from persistent import Persistent
from random import random
from thread import allocate_lock
from types import StringTypes

from zope.exceptions.exceptionformatter import format_exception
from zope.interface import implements
from zope.app.site.interfaces import ISimpleService
from zope.app.container.contained import Contained
from interfaces import IErrorReportingService, ILocalErrorReportingService

#Restrict the rate at which errors are sent to the Event Log
_rate_restrict_pool = {}

# The number of seconds that must elapse on average between sending two
# exceptions of the same name into the the Event Log. one per minute.
_rate_restrict_period = 60

# The number of exceptions to allow in a burst before the above limit
# kicks in. We allow five exceptions, before limiting them to one per
# minute.
_rate_restrict_burst = 5

# _temp_logs holds the logs.
_temp_logs = {}  # { oid -> [ traceback string ] }

cleanup_lock = allocate_lock()

class ErrorReportingService(Persistent, Contained):
    """Error Reporting Service
    """
    implements(IErrorReportingService,
               ILocalErrorReportingService,
               ISimpleService,
               )

    keep_entries = 20
    copy_to_zlog = 0
    _ignored_exceptions = ('Unauthorized',)


    def _getLog(self):
        """Returns the log for this object.
        Careful, the log is shared between threads.
        """
        log = _temp_logs.get(self._p_oid, None)
        if log is None:
            log = []
            _temp_logs[self._p_oid] = log
        return log

    # Exceptions that happen all the time, so we dont need
    # to log them. Eventually this should be configured
    # through-the-web.
    def raising(self, info, request=None):
        """Log an exception.
        Called by ZopePublication.handleException method.
        """
        now = time.time()
        try:
            tb_text = None
            tb_html = None

            strtype = str(getattr(info[0], '__name__', info[0]))
            if strtype in self._ignored_exceptions:
                return

            if not isinstance(info[2], StringTypes):
                tb_text = ''.join(
                        format_exception(*info, **{'as_html': 0}))
                tb_html = ''.join(
                    format_exception(*info, **{'as_html': 1}))
            else:
                tb_text = info[2]

            url = None
            username = None
            req_html = None
            if request:
                # XXX: Temporary fix, which Steve should undo. URL is
                #      just too HTTPRequest-specific.
                if hasattr(request, 'URL'):
                    url = request.URL
                try:
                    # XXX: UnauthenticatedPrincipal does not have getLogin()
                    if hasattr(request.principal, 'getLogin'):
                        login = request.principal.getLogin()
                    else:
                        login = 'unauthenticated'
                    username = ', '.join(map(str, (login,
                                          request.principal.id,
                                          request.principal.title,
                                          request.principal.description
                                         )))
                # When there's an unauthorized access, request.principal is
                # not set, so we get an AttributeError
                # XXX is this right? Surely request.principal should be set!
                # XXX Answer: Catching AttributeError is correct for the
                #             simple reason that UnauthenticatedUser (which
                #             I always use during coding), has no 'getLogin()'
                #             method. However, for some reason this except
                #             does **NOT** catch these errors.
                except AttributeError:
                    pass

                req_html = ''.join(['%s : %s<br>' % item
                                    for item in request.items()])
            try:
                strv = str(info[1])
            # A call to str(obj) could raise anything at all.
            # We'll ignore these errors, and print something
            # useful instead, but also log the error.
            except:
                logging.getLogger('SiteError').exception(
                    'Error in ErrorReportingService while getting a str '
                    'representation of an object')
                strv = '<unprintable %s object>' % (
                        str(type(info[1]).__name__)
                        )

            log = self._getLog()
            entry_id = str(now) + str(random()) # Low chance of collision

            log.append({
                'type': strtype,
                'value': strv,
                'time': time.ctime(now),
                'id': entry_id,
                'tb_text': tb_text,
                'tb_html': tb_html,
                'username': username,
                'url': url,
                'req_html': req_html,
                })
            cleanup_lock.acquire()
            try:
                if len(log) >= self.keep_entries:
                    del log[:-self.keep_entries]
            finally:
                cleanup_lock.release()

            if self.copy_to_zlog:
                self._do_copy_to_zlog(now, strtype, str(url), info)
        finally:
            info = None

    def _do_copy_to_zlog(self, now, strtype, url, info):
        # XXX info is unused; logging.exception() will call sys.exc_info()
        # work around this with an evil hack
        when = _rate_restrict_pool.get(strtype,0)
        if now > when:
            next_when = max(when,
                            now - _rate_restrict_burst*_rate_restrict_period)
            next_when += _rate_restrict_period
            _rate_restrict_pool[strtype] = next_when
            try:
                raise info[0], info[1], info[2]
            except:
                logging.getLogger('SiteError').exception(str(url))

    def getProperties(self):
        return {
            'keep_entries': self.keep_entries,
            'copy_to_zlog': self.copy_to_zlog,
            'ignored_exceptions': self._ignored_exceptions,
            }

    def setProperties(self, keep_entries, copy_to_zlog=0,
                      ignored_exceptions=()):
        """Sets the properties of this site error log.
        """
        copy_to_zlog = bool(copy_to_zlog)
        self.keep_entries = int(keep_entries)
        self.copy_to_zlog = copy_to_zlog
        self._ignored_exceptions = tuple(
                filter(None, map(str, ignored_exceptions))
                )

    def getLogEntries(self):
        """Returns the entries in the log, most recent first.

        Makes a copy to prevent changes.
        """
        res = [entry.copy() for entry in self._getLog()]
        res.reverse()
        return res

    def getLogEntryById(self, id):
        """Returns the specified log entry.
        Makes a copy to prevent changes.  Returns None if not found.
        """
        for entry in self._getLog():
            if entry['id'] == id:
                return entry.copy()
        return None

class RootErrorReportingService(ErrorReportingService):
    rootId = 'root'
    
    def _getLog(self):
        """Returns the log for this object.
        Careful, the log is shared between threads.
        """
        log = _temp_logs.get(self.rootId, None)
        if log is None:
            log = []
            _temp_logs[self.rootId] = log
        return log

globalErrorReportingService = RootErrorReportingService()

def _cleanup_temp_log():
    _temp_logs.clear()

_clear = _cleanup_temp_log
# Register our cleanup with Testing.CleanUp to make writing unit tests simpler.
from zope.testing.cleanup import addCleanUp
addCleanUp(_clear)
del addCleanUp
