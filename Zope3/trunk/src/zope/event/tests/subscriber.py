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

Revision information:
$Id: subscriber.py,v 1.2 2002/12/25 14:13:38 jim Exp $
"""


class DummySubscriber:

    def __init__(self):
        self.notified = 0

    def notify(self, event):
        self.notified += 1

subscriber = DummySubscriber()

class DummyFilter:

    def __init__(self,value=1):
        self.value = value

    def __call__(self, event):
        return self.value

filter = DummyFilter
