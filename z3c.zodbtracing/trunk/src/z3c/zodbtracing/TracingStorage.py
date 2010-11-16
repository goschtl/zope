##############################################################################
#
# Copyright (c) 2005-2006 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""A ZODB storage that allows tracing the calls going to the real storage.

"""
__docformat__ = "reStructuredText"

from zope.interface import implements
from zope.event import notify
from zope.proxy import getProxiedObject, non_overridable
from zope.proxy.decorator import SpecificationDecoratorBase

from z3c.zodbtracing import events

class TracingStorage(SpecificationDecoratorBase):
    """A storage to support tracing the calls going to the real storage."""

    # Proxies can't have a __dict__ so specifying __slots__ here allows
    # us to have instance attributes explicitly on the proxy.
    __slots__ = ('statCollector')

    def __new__(self, storage, statCollector=None):
        return SpecificationDecoratorBase.__new__(self, storage)

    def __init__(self, storage, statCollector=None):
        SpecificationDecoratorBase.__init__(self, storage)
        
        self.statCollector = statCollector
        
        if self.statCollector is not None:
            self.statCollector.initCalled()

    @non_overridable
    def __repr__(self):
        normal_storage = getProxiedObject(self)
        return '<TracingStorage proxy for %r at %s>' % (normal_storage,
                                                     hex(id(self)))
    
    def methodCalled(self, name, *arg, **kw):
        unproxied = getProxiedObject(self)
        func = getattr(unproxied, name)
        result = func(*arg, **kw)
        
        if self.statCollector is not None:
            self.statCollector.methodCalled(name, result, *arg, **kw)
        
        eventKlass = events.EVENTMAP[name]
        eventObj = eventKlass(result, *arg, **kw)
        notify(eventObj)
        return result
    
    @non_overridable
    def load(self, *arg, **kw):
        return self.methodCalled('load', *arg, **kw)

    @non_overridable
    def store(self, *arg, **kw):
        return self.methodCalled('store', *arg, **kw)
    
    @non_overridable
    def close(self, *arg, **kw):
        return self.methodCalled('close', *arg, **kw)
    
    @non_overridable
    def cleanup(self, *arg, **kw):
        return self.methodCalled('cleanup', *arg, **kw)
    
    @non_overridable
    def lastSerial(self, *arg, **kw):
        return self.methodCalled('lastSerial', *arg, **kw)
    
    @non_overridable
    def lastTransaction(self, *arg, **kw):
        return self.methodCalled('lastTransaction', *arg, **kw)