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
$Id: annotatableadapter.py,v 1.2 2002/12/25 14:12:50 jim Exp $
"""

__metaclass__ = type

from zope.component import getAdapter
from zope.app.interfaces.annotation import IAnnotations
from zope.app.interfaces.annotation import IAnnotatable
from zope.app.dublincore.zopedublincore import ZopeDublinCore
from persistence.dict import PersistentDict

DCkey = "zope.app.dublincore.ZopeDublinCore"

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
