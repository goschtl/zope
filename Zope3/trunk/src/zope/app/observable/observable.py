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
"""Observable adapter

$Id$
"""
from zope.interface import implements, providedBy
from zope.app.observable.interfaces import IObservable
from zope.app.annotation.interfaces import IAnnotations
from zope.app.observable.observers import Observers

key = 'zope.app.observable'

class ObservableAdapter:

    implements(IObservable)
    
    def __init__(self, context):
        self.context = context

    def subscribe(self, required, provided, subscriber):
        annotations = IAnnotations(self.context)
        registry = annotations.get(key)
        
        if registry is None:
            annotations[key] = registry = Observers()

        registry.subscribe(required, provided, subscriber)

    def unsubscribe(self, required, provided, subscriber):
        annotations = IAnnotations(self.context)
        registry = annotations.get(key)

        if registry is not None:
            # if there is no registry, we can't unsubscribe
            registry.unsubscribe(required, provided, subscriber)

    def notify(self, event, provided):
        annotations = IAnnotations(self.context)
        registry = annotations.get(key)

        if registry is not None:
            for subscriber in registry.subscriptions([providedBy(event)],
                                                     provided):
                subscriber.notify(event)
