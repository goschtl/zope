##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""DAV Opaque properties implementation details

Opaque properties are arbitrary propterties set trhough DAV and which have no
special meaning to the Zope application.

$Id$
"""
__docformat__ = 'restructuredtext'

from UserDict import DictMixin

from zope.interface import implements
from zope.app.annotation.interfaces import IAnnotations, IAnnotatable
from zope.app.location import Location

from interfaces import IDAVOpaqueNamespaces

from BTrees.OOBTree import OOBTree

DANkey = "zope.app.dav.DAVOpaqueProperties"

class DAVOpaqueNamespacesAdapter(DictMixin, Location):
    """Adapt annotatable objects to DAV opaque property storage."""

    implements(IDAVOpaqueNamespaces)
    __used_for__ = IAnnotatable

    annotations = None

    def __init__(self, context):
        annotations = IAnnotations(context)
        oprops = annotations.get(DANkey)
        if oprops is None:
            self.annotations = annotations
            oprops = OOBTree()

        self._mapping = oprops

    def _changed(self):
        if self.annotations is not None:
            self.annotations[DANkey] = self._mapping
            self.annotations = None

    def get(self, key, default=None):
        return self._mapping.get(key, default)

    def __getitem__(self, key):
        return self._mapping[key]

    def keys(self):
        return self._mapping.keys()

    def __setitem__(self, key, value):
        self._mapping[key] = value
        self._changed()

    def __delitem__(self, key):
        del self._mapping[key]
        self._changed()

    #
    # methods that simplify the reteriving of dead properties.
    #

    def hasProperty(self, namespace, name):
        if self._mapping.has_key(namespace):
            return self._mapping[namespace].has_key(name)
        return False

    def getProperty(self, namespace, name):
        return self._mapping[namespace][name]

    def setProperty(self, namespace, name, propval):
        if not self.hasProperty(namespace, name):
            if not self.has_key(namespace):
                self[namespace] = OOBTree()
        ns = self[namespace]
        ns[name] = propval

    def removeProperty(self, namespace, name):
        if self.hasProperty(namespace, name):
            del self[namespace][name]
            if not self[namespace]:
                del self[namespace]
