##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Implement zope-specific event dispatching, based on subscription adapters

This package instals an event dispatcher that calls event handlers,
registered as subscription adapters providing None.

So, to subscribe to an event, use a subscription adapter to None:

  >>> from zope.app.tests.placelesssetup import setUp, tearDown
  >>> setUp()

  >>> class E1:
  ...     pass

  >>> class E2(E1):
  ...     pass

  >>> called = []
  >>> def handler1(event):
  ...     called.append(1)

  >>> def handler2(event):
  ...     called.append(2)

  >>> from zope.app.tests import ztapi
  >>> from zope.interface import implementedBy
  >>> ztapi.handle([implementedBy(E1)], handler1)
  >>> ztapi.handle([implementedBy(E2)], handler2)

  >>> from zope.event import notify

  >>> notify(E1())
  >>> called
  [1]

  >>> del called[:]
  >>> notify(E2())
  >>> called.sort()
  >>> called
  [1, 2]
  
  >>> tearDown()

$Id$
"""

from zope.component import subscribers
import zope.event

def dispatch(*event):
    for ignored in subscribers(event, None):
        pass

zope.event.subscribers.append(dispatch)

def publish(context, event):
    zope.event.notify(event)
