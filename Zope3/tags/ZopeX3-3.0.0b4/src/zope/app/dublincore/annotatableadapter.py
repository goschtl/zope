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
"""Dublin Core Annotatable Adapter

$Id$
"""
__docformat__ = 'restructuredtext'

from persistent.dict import PersistentDict

from zope.app.annotation.interfaces import IAnnotations, IAnnotatable
from zope.app.dublincore.zopedublincore import ZopeDublinCore
from zope.app.location import Location


DCkey = "zope.app.dublincore.ZopeDublinCore"


class ZDCAnnotatableAdapter(ZopeDublinCore, Location):
    """Adapt annotatable objects to Zope Dublin Core."""

    __used_for__ = IAnnotatable

    annotations = None

    def __init__(self, context):
        annotations = IAnnotations(context)
        dcdata = annotations.get(DCkey)
        if dcdata is None:
            self.annotations = annotations
            dcdata = ZDCAnnotationData()

        super(ZDCAnnotatableAdapter, self).__init__(dcdata)

    def _changed(self):
        if self.annotations is not None:
            self.annotations[DCkey] = self._mapping
            self.annotations = None

__doc__ = ZDCAnnotatableAdapter.__doc__ + __doc__


class ZDCAnnotationData(PersistentDict):
    """Data for a Dublin Core annotation.

    A specialized class is used to allow an alternate fssync
    serialization to be registered.  See the
    zope.app.dublincore.fssync package.
    """
