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
$Id: annotatableadapter.py,v 1.5 2004/01/13 19:32:19 fdrake Exp $
"""

__metaclass__ = type

from zope.component import getAdapter
from zope.fssync.server.entryadapter import ObjectEntryAdapter
from zope.fssync.server.interfaces import IObjectFile
from zope.interface import implements
from zope.app.interfaces.annotation import IAnnotations
from zope.app.interfaces.annotation import IAnnotatable
from zope.app.dublincore.zopedublincore import ZopeDublinCore
from zope.xmlpickle import dumps, loads
from persistence.dict import PersistentDict

DCkey = "zope.app.dublincore.ZopeDublinCore"

class ZDCAnnotatableAdapter(ZopeDublinCore):
    """Adapt annotatable objects to Zope Dublin Core."""

    __used_for__ = IAnnotatable

    annotations = None

    def __init__(self, context):
        annotations = getAdapter(context, IAnnotations)
        dcdata = annotations.get(DCkey)
        if not dcdata:
            self.annotations = annotations
            dcdata = ZDCAnnotationData()
        elif not isinstance(dcdata, ZDCAnnotationData):
            # Convert mapping to a ZDCAnnotationData, and set things
            # up so that the annotations object is only updated the
            # first time we're writing to it; this avoids converting
            # it when we wouldn't otherwise write to the object.
            self.annotations = annotations
            d = ZDCAnnotationData()
            d.update(dcdata)
            dcdata = d

        super(ZDCAnnotatableAdapter, self).__init__(dcdata)

    def _changed(self):
        if self.annotations is not None:
            self.annotations[DCkey] = self._mapping
            self.annotations = None

__doc__ = ZDCAnnotatableAdapter.__doc__ + __doc__


class ZDCAnnotationData(PersistentDict):
    pass


class ZDCAnnotationDataAdapter(ObjectEntryAdapter):

    implements(IObjectFile)

    def getBody(self):
        return dumps(self.context.data)

    def setBody(self, data):
        data = loads(data)
        self.context.clear()
        self.context.update(data)
