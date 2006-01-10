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
"""Cron-like Scheduler Task

$Id$
"""
__docformat__ = "reStructuredText"

import time
import zope.interface
from twisted.internet import reactor
from scheduler import interfaces, task

class CronTask(task.Task):

    zope.interface.implements(interfaces.ICronTask)

    # Set a four year timeout to find the next scheduled time
    timeout = 4*60*60*24*365

    def __init__(self, callable, arguments=(), keywords={},
                 minute=(), hour=(), dayOfMonth=(), month=(), dayOfWeek=()):
        super(CronTask, self).__init__(callable, arguments, keywords)

        # See scheduler.interfaces.ICronTask
        self.minute = minute
        self.hour = hour
        self.dayOfMonth = dayOfMonth
        self.month = month
        self.dayOfWeek = dayOfWeek


    def computeDelayToNextCall(self):
        """See scheduler.interfaces.ITask"""
        now = next = time.time()
        while next <= now+self.timeout:
            next += 60
            fields = time.localtime(next)

            if ((self.month and fields[1] not in self.month) or
                (self.dayOfMonth and fields[2] not in self.dayOfMonth) or
                (self.dayOfWeek and fields[6] % 7 not in self.dayOfWeek) or
                (self.hour and fields[3] not in self.hour) or
                (self.minute and fields[4] not in self.minute)):

                continue

            return next

        raise SomeError
