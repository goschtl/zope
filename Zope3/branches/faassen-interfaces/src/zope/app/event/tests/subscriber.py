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
This contains some dummy stuff to do with subscribing to event channels
that's useful in several test modules.

$Id: subscriber.py,v 1.4 2004/03/02 18:50:59 philikon Exp $
"""
from zope.app.event.interfaces import IFilter, ISubscriber
from zope.interface import implements

class DummySubscriber:

    implements(ISubscriber)

    def __init__(self):
        self.notified = 0

    def notify(self, event):
        self.notified += 1

subscriber = DummySubscriber()

class DummyFilter:
    implements(IFilter)

    def __init__(self,value=1):
        self.value = value

    def __call__(self, event):
        return self.value

filter = DummyFilter
