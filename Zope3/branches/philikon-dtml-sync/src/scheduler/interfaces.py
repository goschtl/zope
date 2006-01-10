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
"""Task Scheduler Interfaces

$Id$
"""
__docformat__ = "reStructuredText"

import zope.schema
from zope.interface import Interface, Attribute


class ITask(Interface):
    """A task that is executed at a particular time."""

    # These names were chosen to match Twisted's LoopingCall class.
    f = Attribute("The callable that is executes at the scheduled time.")

    a = zope.schema.Tuple(
        title=u"Arguments",
        description=u"Arguments (tuple) for the callable.")

    kw = zope.schema.Dict(
        title=u"Keywords",
        description=u"Keywords (dict) for the callable.")

    starttime = zope.schema.Float(
        title=u"Start Time",
        description=u"Time in seconds at which the task will be first "
                    u"scheduled.")

    running = zope.schema.Bool(
        title=u"Is Running",
        description=u"Tells you whether a task is running or not.",
        default=False)

    def start():
        """Start to schedule the task."""

    def stop():
        """Stop running the task."""
        
    def computeDelayToNextCall():
        """Calculate the delay to the next execution of this task.

        The returned value should be a float or integer that specifies the
        time in seconds. Note that not all operating systems support floating
        points.
        """

    def __call__():
        """Execute the task and reschedule it."""


class ITaskStatistic(Interface):
    """Keeps track of statistical information about the task."""

    count = zope.schema.Int(
        title=u"Execution Counter",
        description=u"Specifies how many times the callable has been executed,"
                    u"since the task was started.",
        default=0)


class ILoopTask(ITask):
    """A task that is executed at a particular interval."""

    timeInterval = zope.schema.Int(
        title=u"Interval",
        description=u"Interval between calls in seconds",
        default=60)


class ICronTask(ITask):
    """A special task that schedules the job based on cron-like information."""

    minute = zope.schema.Tuple(
        title=u"Minute",
        description=u"The minute (list) to run the task.",
        value_type=zope.schema.Int(min=0, max=59)
        )

    hour = zope.schema.Tuple(
        title=u"Hour",
        description=u"The hour (list) to run the task.",
        value_type=zope.schema.Int(min=0, max=23)
        )

    dayOfMonth = zope.schema.Tuple(
        title=u"Day of Month",
        description=u"The day of month (list) to run the task.",
        value_type=zope.schema.Int(min=1, max=31)
        )

    month = zope.schema.Tuple(
        title=u"Month",
        description=u"The month (list) to run the task.",
        value_type=zope.schema.Int(min=1, max=12)
        )

    dayOfWeek = zope.schema.Tuple(
        title=u"Day of Week",
        description=u"The day of week (list) to run the task.",
        value_type=zope.schema.Int(min=0, max=7)
        )
