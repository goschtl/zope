##############################################################################
#
# Copyright (c) 2006 Lovely Systems and Contributors.
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
"""Task Service Implementation

$Id$
"""
__docformat__ = 'restructuredtext'

import time
import datetime
import persistent
import zope.interface
from zope.schema.fieldproperty import FieldProperty
from lovely.remotetask import interfaces


class Job(persistent.Persistent):
    """A simple, non-persistent task implementation."""
    zope.interface.implements(interfaces.IJob)

    id = FieldProperty(interfaces.IJob['id'])
    task = FieldProperty(interfaces.IJob['task'])
    status = FieldProperty(interfaces.IJob['status'])
    input = FieldProperty(interfaces.IJob['input'])
    output = FieldProperty(interfaces.IJob['output'])
    error = FieldProperty(interfaces.IJob['error'])
    created = FieldProperty(interfaces.IJob['created'])
    started = FieldProperty(interfaces.IJob['started'])
    completed = FieldProperty(interfaces.IJob['completed'])

    def __init__(self, id, task, input):
        self.id = id
        self.task = task
        self.input = input
        self.created = datetime.datetime.now()

    def __repr__(self):
        return '<%s %r>' %(self.__class__.__name__, self.id)


class CronJob(Job):
    """A job for reocuring tasks"""
    zope.interface.implements(interfaces.ICron)

    minute = FieldProperty(interfaces.ICron['minute'])
    hour = FieldProperty(interfaces.ICron['hour'])
    dayOfMonth = FieldProperty(interfaces.ICron['dayOfMonth'])
    month = FieldProperty(interfaces.ICron['month'])
    dayOfWeek = FieldProperty(interfaces.ICron['dayOfWeek'])

    _lastExecutionTime = None

    def __init__(self, id, task, input,
                 minute=(),
                 hour=(),
                 dayOfMonth=(),
                 month=(),
                 dayOfWeek=(),
                ):
        super(CronJob, self).__init__(id, task, input)
        self.minute = minute
        self.hour = hour
        self.dayOfMonth = dayOfMonth
        self.month = month
        self.dayOfWeek = dayOfWeek

    def timeOfNextCall(self, now=None):
        if now is None:
            now = time.time()
        next = now
        inc = lambda t: 60
        lnow = list(time.localtime(now)[:5])
        if self.minute:
            pass
        elif self.hour:
            inc = lambda t: 60*60
            lnow = lnow[:4]
        elif self.dayOfMonth:
            inc = lambda t: 24*60*60
            lnow = lnow[:3]
        elif self.dayOfWeek:
            inc = lambda t: 24*60*60
            lnow = lnow[:3]
        elif self.month:
            mlen = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
            def minc(t):
                m = time.localtime(t)[1] - 1
                if m == 1:
                    # see if we have a leap year
                    y = time.localtime(t)[0]
                    if y % 4 != 0:
                        d = 28
                    elif y % 400 == 0:
                        d = 29
                    elif y % 100 == 0:
                        d = 28
                    else:
                        d = 29
                    return d*24*60*60
                return mlen[m]*24*60*60
            inc = minc
            lnow = lnow[:3]
            lnow[2] = 1
        while len(lnow)<9:
            lnow.append(0)
        while next <= now+365*24*60*60:
            next += inc(next)
            fields = time.localtime(next)
            if ((self.month and fields[1] not in self.month) or
                (self.dayOfMonth and fields[2] not in self.dayOfMonth) or
                (self.dayOfWeek and fields[6] % 7 not in self.dayOfWeek) or
                (self.hour and fields[3] not in self.hour) or
                (self.minute and fields[4] not in self.minute)):
                continue
            return int(next)
        return None

