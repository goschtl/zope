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
"""Subview helper implementations

$Id$
"""

import persistent
import persistent.dict
import persistent.interfaces
from zope import interface
from zope.subview import interfaces
import zope.security.management
import zope.security.proxy
from zope.publisher.interfaces import IRequest

class SubviewBase(persistent.Persistent):
    interface.implements(interfaces.ISubview)

    context = request = name = parent = None

    @property
    def prefix(self):
        if self.name is None or self.parent is None:
            raise ValueError('name and parent must be set')
        return '%s.%s' % (self.parent.prefix, self.name)

    def render(self):
        if not self._initialized:
            raise RuntimeError('Initialize subview first')
         # subclases should render now

    _initialized=False
    def update(self, parent=None, name=None):
        self._initialized = True
        if parent is not None:
            self.parent = parent
        if name is not None:
            self.name = name
        if self.parent is None or self.name is None:
            raise RuntimeError(
                "parent and name must be set or passed in to update")
        # subclasses should calculate state now!

def getRequest():
    i = zope.security.management.getInteraction() # raises NoInteraction
    for p in i.participations:
        if IRequest.providedBy(p):
            return p
    raise RuntimeError('No IRequest in interaction')

ANNOTATIONS_KEY = 'zope.subview'

PersistentSubviewBase(persistent.Persistent, SubviewBase):

    interface.implements(interfaces.IPersistentSubview)

    @property
    def context(self):
        # avoid persisting possible security wrappers; avoid possible conflict
        # errors
        return self.parent.context

    @property
    def request(self):
        # avoid persisting the request; avoid possible conflict errors
        return getRequest()

    _parent = None
    @apply
    def parent():
        # we store persistent parents on this object, only changing when
        # necessary so as not to invite conflict errors unnecessarily.  we
        # store non-persistent parents in the request, so that the parent
        # is not persisted and so that we again do not invite conflict errors.
        # we use id(self) because a request is not persistent: we are only
        # stashing the id while the object is in memory, so we should be fine.
        def get(self):
            if self._parent is not None:
                return self._parent
            else:
                parents = self.request.annotations.get(ANNOTATIONS_KEY)
                if parents is not None:
                    return parents.get(id(self))
            return None
        def set(self, value):
            # parent views should typically be unproxied, but just to be sure:
            value = zope.security.proxy.removeSecurityProxy(value)
            # if it is a persistent object...
            if persistent.interfaces.IPersistent.providedBy(value):
                # ...and we haven't stored it before (avoid conflict errors)
                # then 
                if value is not self._parent:
                    self._parent = value
            else:
                if self._parent is not None: # avoid conflict errors
                    self._parent = None
                parents = self.request.annotations.setdefault(
                    ANNOTATIONS_KEY, [])
                parents[id(self)] = value
        return property(get, set)

class IntermediateSubviewMixin(object):

    def getSubview(self, name):
        raise NotImplementedError

    def iterSubviews(self):
        raise NotImplementedError

    def update(parent=None, name=None):
        super(IntermediateSubviewMixin, self).update(parent, name)
        for key, val in self.iterSubviews:
            val.update(self, key)

    def getSubviewByPrefix(self, prefix):
        # somewhat naive but probably sufficient implementation
        if prefix == self.prefix:
            return self
        if (prefix.startswith(self.prefix) or
            prefix.startswith('zope.subview.')):
            for key, val in self.iterSubviews:
                if interfaces.ISubviewContainer.providedBy(val):
                    res = val.getSubviewByPrefix(prefix)
                    if res is not None:
                        return res
                elif val.prefix == prefix:
                    return res

class IntermediateSubviewBase(IntermediateSubviewMixin, SubviewBase):
    interface.implements(interfaces.IIntermediateSubview)

class PersistentIntermediateSubviewBase(
    IntermediateSubviewMixin, PersistentSubviewBase):
    interface.implements(interfaces.IPersistentIntermediateSubview)
