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
"""Objects that take care of annotating dublin core meta data times

$Id: timeannotators.py,v 1.5 2003/10/23 19:04:09 garrett Exp $
"""
__metaclass__ = type

from datetime import datetime
from zope.component import queryAdapter
from zope.app.interfaces.dublincore import IZopeDublinCore
from zope.app.interfaces.event import ISubscriber
from zope.interface import implements

class DCTimeAnnotatorBase:
    """Update Dublin-Core time property
    """
    implements(ISubscriber)

    def notify(self, event):
        dc = queryAdapter(event.object, IZopeDublinCore)
        if dc is not None:
            self.annotate(dc)

    def annotate(self, dc):
        raise RuntimeError, 'annotate not implemented'


class ModifiedAnnotatorClass(DCTimeAnnotatorBase):
    """Updates DC modified when an object is modified."""

    def annotate(self, dc):
        dc.modified = datetime.utcnow()


class CreatedAnnotatorClass(DCTimeAnnotatorBase):
    """Sets DC created and modified when an object is created."""

    def annotate(self, dc):
        now = datetime.utcnow()
        dc.created = now
        dc.modified = now


ModifiedAnnotator = ModifiedAnnotatorClass()
CreatedAnnotator = CreatedAnnotatorClass()
