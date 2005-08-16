##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Tests for the Observable event infrastructure.

$Id$
"""

import doctest
import unittest

from zope.interface import implements
from zope.app.observable.observable import ObservableAdapter, key
from zope.app.observable.interfaces import IObservable
from zope.app.annotation.interfaces import IAnnotations
from zope.app.container.interfaces import IObjectAddedEvent
from zope.app.container.interfaces import IObjectRemovedEvent
from zope.app.observable import observerevent

class DummyAnnotationsClass(dict):
    implements(IAnnotations)


class DummyEvent(object):
    implements(IObjectAddedEvent)
    
def test_handle():
    """
    First create an annotatable object and an adapter

      >>> obj = DummyAnnotationsClass()
      >>> adapter = ObservableAdapter(obj)

    Make a handler and make a faux subscription

      >>> def handler(event):
      ...     pass

      >>> adapter.handle([IObjectAddedEvent], handler)

    Make sure an ObjectAdapterRegistry was created

      >>> obj[key] is not None
      True

    Make sure the registry contains a subscription for the correct event

      >>> IObjectAddedEvent in obj[key].adapters
      True

    """

def test_unhandle():
    """
    First create an annotatable object and an adapter

      >>> obj = DummyAnnotationsClass()
      >>> adapter = ObservableAdapter(obj)

    Make a handler and make a faux subscription

      >>> def handler(event):
      ...     pass
      >>> adapter.handle([IObjectAddedEvent], handler)

    Now unhandle from the registry

      >>> adapter.unhandle([IObjectAddedEvent], handler)

    There should be no handlers for IObjectAddedEvent after unsubscription.

      >>> obj[key].adapters[IObjectAddedEvent]
      {}
    """

def test_notify():
    """
    First create an annotatable object and an adapter

      >>> obj = DummyAnnotationsClass()
      >>> adapter = ObservableAdapter(obj)

    Make a handler and make a faux subscription

      >>> events = []
      >>> def handler(event):
      ...     events.append(event)
      >>> adapter.handle([IObjectAddedEvent], handler)

    Make sure an ObjectAdapterRegistry was created

      >>> obj[key] is not None
      True

    Call notify

      >>> event = DummyEvent()
      >>> adapter.notify(event)
      >>> events == [event]
      True

    """

class DummyObservable(object):
    implements(IObservable)

    def __init__(self):
        self.flag = False

    def notify(self, event):
        self.flag = True

class DummyNotObservable(object):
    
    def __init__(self):
        self.flag = False
        
    def notify(self, event):
        self.flag = True

class DummyObservableEvent(object):
    implements(IObjectRemovedEvent, IObservable)

    def __init__(self):
        self.object = DummyObservable()

class DummyNotObservableEvent(object):
    implements(IObjectRemovedEvent)
    
    def __init__(self):
        self.object = DummyNotObservable()

def testObservableEvents(self):
    """
    When an object that has subscriptions change, the
    handlers are notified.

    >>> event = DummyObservableEvent()
    >>> observerevent.observerEventNotifier(event)
    >>> event.object.flag
    True
    """

def testNotObservableEvents(self):
    """

    When an object that has no subscriptions changes, the
    ObserverEventNotifier doesn't do anything to it.

    >>> event = DummyNotObservableEvent()
    >>> observerevent.observerEventNotifier(event)
    >>> event.object.flag
    False
    """

def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite(),
        doctest.DocTestSuite('zope.app.observable.observers'),
        ))

if __name__ == '__main__':
    test_suite()
