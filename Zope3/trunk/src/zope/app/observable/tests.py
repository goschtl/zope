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
"""Tests for the Observable Adapter.

$Id: tests.py,v 1.2 2004/03/30 14:13:57 nathan Exp $
"""

import doctest
import unittest

from zope.interface import implements
from zope.app.observable.observable import ObservableAdapter, key
from zope.app.observable.interfaces import IObservable
from zope.app.event.interfaces import ISubscriber
from zope.app.annotation.interfaces import IAnnotations
from zope.app.container.interfaces import IObjectAddedEvent

class DummyAnnotationsClass(dict):
    implements(IAnnotations)

class DummySubscriber:

    implements(ISubscriber)

    def __init__(self):
        self.events = []
        
    def notify(self, event):

        self.events.append(event)

class DummyEvent:
    implements(IObjectAddedEvent)
    
def test_subscribe():
    """
    First create an annotatable object and an adapter
    >>> obj = DummyAnnotationsClass()
    >>> adapter = ObservableAdapter(obj)

    Make a subscriber and make a faux subscription
    >>> subscriber = DummySubscriber()
    >>> adapter.subscribe([IObjectAddedEvent], ISubscriber, subscriber)

    Make sure an ObjectAdapterRegistry was created
    >>> obj[key] is not None
    True

    Make sure the registry contains a subscription for the correct event
    >>> IObjectAddedEvent in obj[key].adapters
    True

    """

def test_unsubscribe():
    """
    First create an annotatable object and an adapter
    >>> obj = DummyAnnotationsClass()
    >>> adapter = ObservableAdapter(obj)

    Make a subscriber and make a faux subscription
    >>> subscriber = DummySubscriber()
    >>> adapter.subscribe([IObjectAddedEvent], ISubscriber, subscriber)

    Now unsubscribe from the registry
    >>> adapter.unsubscribe([IObjectAddedEvent], ISubscriber, subscriber)

    There should be no subscribers for IObjectAddedEvent after unsubscription.
    >>> obj[key].adapters[IObjectAddedEvent]
    {}
    """

def test_notify():
    """
    First create an annotatable object and an adapter
    >>> obj = DummyAnnotationsClass()
    >>> adapter = ObservableAdapter(obj)

    Make a subscriber and make a faux subscription
    >>> subscriber = DummySubscriber()
    >>> adapter.subscribe([IObjectAddedEvent], ISubscriber, subscriber)

    Make sure an ObjectAdapterRegistry was created
    >>> obj[key] is not None
    True

    Call notify
    >>> event = DummyEvent()
    >>> adapter.notify(event, ISubscriber)
    >>> subscriber.events == [event]
    True
    """

def test_suite():
    import sys
    return unittest.TestSuite((
        doctest.DocTestSuite(),
        doctest.DocTestSuite('zope.app.observable.observers'),
        ))

if __name__ == '__main__':
    test_suite()
    
