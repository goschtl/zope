##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""DAV Opaque Properties Annotatable Adapter

$Id: annotatableadapter.py 26734 2004-07-23 21:55:49Z pruggera $
"""
__docformat__ = 'restructuredtext'

from BTrees.OOBTree import OOBTree

from zope.app.annotation.interfaces import IAnnotations, IAnnotatable
from zope.app.dav.opaquenamespaces import DAVOpaqueNamespaces
from zope.app.location import Location

DANkey = "zope.app.dav.DAVOpaqueProperties"


class DAVOpaqueNamespacesAdapter(DAVOpaqueNamespaces, Location):
    """Adapt annotatable objects to DAV opaque property storage."""

    __used_for__ = IAnnotatable

    annotations = None

    def __init__(self, context):
        annotations = IAnnotations(context)
        oprops = annotations.get(DANkey)
        if oprops is None:
            self.annotations = annotations
            oprops = OOBTree()

        super(DAVOpaqueNamespacesAdapter, self).__init__(oprops)

    def _changed(self):
        if self.annotations is not None:
            self.annotations[DANkey] = self._mapping
            self.annotations = None
