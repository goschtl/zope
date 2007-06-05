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
"""Scheduler Task

$Id$
"""
__docformat__ = "reStructuredText"

import time
import zope.interface
from twisted.internet import defer, task, reactor
from twisted.python import reflect

from scheduler import interfaces

class Task(task.LoopingCall):

    zope.interface.implements(interfaces.ITask, interfaces.ITaskStatistic)

    def __init__(self, callable, arguments=(), keywords={}):
        task.LoopingCall.__init__(self, callable, *arguments, **keywords)


    def start(self, now=False):
        """See scheduler.interfaces.ITask"""
        # The LoopingCall implementation sucks, so we make it better. :) The
        # interval can be anything, since we ignore it anyways.
        task.LoopingCall.start(self, 0, now)

    def computeDelayToNextCall(self):
        """See scheduler.interfaces.ITask"""
        raise NotImplemented, \
              'Please implement `computeDelayToNextCall()` in a sub-class.'


    def _reschedule(self):
        """Schedule the next task execution."""
        delay = self.computeDelayToNextCall()

        if delay == 0:
            self.call = reactor.callLater(0, self)
        else:
            self.call = reactor.callLater(delay, self)

    def __repr__(self):
        if hasattr(self.f, 'func_name'):
            func = self.f.func_name
            if hasattr(self.f, 'im_class'):
                func = self.f.im_class.__name__ + '.' + func
        else:
            func = reflect.safe_repr(self.f)

        return '%s(%s, *%s, **%s)' % (
            self.__class__.__name__, func, reflect.safe_repr(self.a),
            reflect.safe_repr(self.kw))
