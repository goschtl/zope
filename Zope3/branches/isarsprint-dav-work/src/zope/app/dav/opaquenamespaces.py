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

from zope.interface import implements

from interfaces import IDAVOpaqueNamespaces


class DAVOpaqueNamespaces(DictMixin):
    """Opaque storage for DAV properties."""
    
    implements(IDAVOpaqueNamespaces)

    def __init__(self, mapping=None):
        if mapping is None:
            mapping = {}
        self._mapping = mapping
        
    def _changed(self):
        self._p_changed = True

    def get(self, key, default=None):
        self._mapping.get(key, default)

    def __getitem__(self, key):
        return self._mapping[key]
        
    def keys(self):
        return self._mapping.keys()
    
    def __setitem__(self, key, value):
        self._mapping[key] = value

    def __delitem__(self, key):
        del self._mapping[key]
