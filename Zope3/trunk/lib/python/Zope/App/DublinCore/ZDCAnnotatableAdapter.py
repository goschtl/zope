##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""
$Id: ZDCAnnotatableAdapter.py,v 1.2 2002/10/04 19:05:50 jim Exp $
"""

__metaclass__ = type

from Zope.ComponentArchitecture import getAdapter
from Zope.App.OFS.Annotation.IAnnotations import IAnnotations
from Zope.App.OFS.Annotation.IAnnotatable import IAnnotatable
from Zope.App.DublinCore.ZopeDublinCore import ZopeDublinCore
from Persistence.PersistentDict import PersistentDict

DCkey = "Zope.App.DublinCore.ZopeDublinCore"

class ZDCAnnotatableAdapter(ZopeDublinCore):
    """Adapt annotatable objects to Zope Dublin Core
    """

    __used_for__ = IAnnotatable

    annotations = None

    def __init__(self, context):
        annotations = getAdapter(context, IAnnotations)
        dcdata = annotations.get(DCkey)
        if not dcdata:
            self.annotations = annotations
            dcdata = PersistentDict()

        super(ZDCAnnotatableAdapter, self).__init__(dcdata)

    def _changed(self):
        if self.annotations is not None:
            self.annotations[DCkey] = self._mapping
            self.annotations = None

__doc__ = ZDCAnnotatableAdapter.__doc__ + __doc__

