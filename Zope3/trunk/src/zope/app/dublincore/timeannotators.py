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

$Id: timeannotators.py,v 1.3 2002/12/30 14:03:00 stevea Exp $
"""
__metaclass__ = type

from datetime import datetime
from zope.component import queryAdapter
from zope.app.interfaces.dublincore import IZopeDublinCore
from zope.app.interfaces.event import ISubscriber

class DCTimeAnnotatorClass:
    """Update Dublin-Core time property
    """
    __implements__ = ISubscriber

    def __init__(self, property):
        self.property = property

    def notify(self, event):
        dc = queryAdapter(event.object, IZopeDublinCore)
        if dc is not None:
            setattr(dc, self.property, datetime.utcnow())

ModifiedAnnotator = DCTimeAnnotatorClass('modified')
CreatedAnnotator = DCTimeAnnotatorClass('created')
