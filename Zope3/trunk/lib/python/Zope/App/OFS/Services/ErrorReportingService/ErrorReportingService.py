##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
# 
##############################################################################
"""

Revision information:
$Id: ErrorReportingService.py,v 1.7 2002/11/11 08:56:45 stevea Exp $
"""

import sys
import time
from random import random
from thread import allocate_lock
from Persistence import Persistent
from types import StringType, UnicodeType
from zLOG import LOG, ERROR
from Zope.Exceptions.ExceptionFormatter import format_exception
from Zope.ContextWrapper import ContextMethod
from Zope.App.OFS.Services.ErrorReportingService.IErrorReportingService \
        import IErrorReportingService

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

class ErrorReportingService(Persistent):
    """Error Reporting Service
    """
    __implements__ = IErrorReportingService

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
    def _makestr(self, dictionary):
        retVal = ''
        for each in dictionary.keys():
            retVal = retVal +str(each)+' : '+str(dictionary[each])+'<br> '
        return retVal
    
    def raising(self, info, request=None):
        """Log an exception.
        Called by ZopePublication.handleException method.
        """
        now = time.time()
        try:
            try:
                tb_text = None
                tb_html = None

                strtype = str(getattr(info[0], '__name__', info[0]))
                if strtype in self._ignored_exceptions:
                    return
                
                if not isinstance(info[2], StringType) and not isinstance(
                    info[2], UnicodeType):
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
                    url = request.URL
                    try:
                       username = ','.join(request.user.getLogin(),
                                           request.user.getId(),
                                           request.user.getTitle(),
                                           request.user.getDescription()
                                           )
                    # XXX bare except clause. Why is this here?
                    # There should be a comment explaining why a bare
                    # except clause is the right thing in this situation.
                    except:
                        pass
                    try:
                        req_html = self._makestr(request)
                    # XXX bare except clause. Why is there here?
                    except:
                        pass
                    
                try:
                    strv = str(info[1])
                # XXX bare except clause. Why is this here?
                except:
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
            # XXX bare except clause. Why is this here?
            except:
                 LOG('SiteError', ERROR, 'Error while logging', 
                     error=sys.exc_info())
            else:
                if self.copy_to_zlog:
                    self._do_copy_to_zlog(now, strtype, str(url), info)
        finally:
            info = None
    raising = ContextMethod(raising)

    def _do_copy_to_zlog(self, now, strtype, url, info):
        when = _rate_restrict_pool.get(strtype,0)
        if now > when:
            next_when = max(when,
                            now - _rate_restrict_burst*_rate_restrict_period)
            next_when += _rate_restrict_period
            _rate_restrict_pool[strtype] = next_when
            LOG('SiteError', ERROR, str(url), error=info)

    def getProperties(self):
        return {
            'keep_entries': self.keep_entries,
            'copy_to_zlog': self.copy_to_zlog,
            'ignored_exceptions': self._ignored_exceptions,
            }
    getProperties = ContextMethod(getProperties)

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
    setProperties = ContextMethod(setProperties)
    def getLogEntries(self):
        """Returns the entries in the log, most recent first.

        Makes a copy to prevent changes.
        """
        res = [entry.copy() for entry in self._getLog()]
        res.reverse()
        return res
    getLogEntries = ContextMethod(getLogEntries)

    def getLogEntryById(self, id):
        """Returns the specified log entry.
        Makes a copy to prevent changes.  Returns None if not found.
        """
        for entry in self._getLog():
            if entry['id'] == id:
                return entry.copy()
        return None
    getLogEntryById = ContextMethod(getLogEntryById)


def _cleanup_temp_log():
    _temp_logs.clear()

_clear = _cleanup_temp_log
# Register our cleanup with Testing.CleanUp to make writing unit tests simpler.
from Zope.Testing.CleanUp import addCleanUp
addCleanUp(_clear)
del addCleanUp
