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
"""Attribute Annotations implementation 

$Id: attribute.py 26632 2004-07-19 14:56:53Z jim $
"""
__docformat__ = 'restructuredtext'

from UserDict import DictMixin
from xml.dom import minidom

from zope.interface import implements
from zope.interface.common.mapping import IMapping
from zope.app.annotation.interfaces import IAnnotations, IAnnotatable
from zope.app.location import Location

from BTrees.OOBTree import OOBTree

DANkey = "zope.app.dav.DAVOpaqueProperties"


class IDAVOpaqueNamespaces(IMapping):
    """Opaque storage for non-registered DAV namespace properties.

    Any unknown (no interface registered) DAV properties are stored opaquely
    keyed on their namespace URI, so we can return them later when requested.
    Thus this is a mapping of a mapping. 

    Property values themselves consist of an attributes structure and the 
    actual opaque value, of the form (((attr1, val1), (attr2, val2)), value) 
    
    """

    
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
    # Convenience methods; storing and retrieving properties through WebDAV
    #
    def renderProperty(self, ns, nsprefix, prop, propel):
        """Render a property as DOM elements"""
        value = self.get(ns, {}).get(prop)
        if value is None:
            return
        value = minidom.parseString(value)
        el = propel.ownerDocument.importNode(value.documentElement, True)
        el.setAttribute('xmlns', nsprefix)
        propel.appendChild(el)
