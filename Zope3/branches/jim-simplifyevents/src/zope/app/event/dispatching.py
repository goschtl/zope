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

  >>> from zope.app.tests.placelesssetup import SetUp, tearDown
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
  >>> ztapi.subscribe(E1, None, handler1)
  >>> ztapi.subscribe(E2, None, handler2)

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
