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
"""Objects that take care of annotating dublin core meta data times

$Id$
"""
__docformat__ = 'restructuredtext'

from datetime import datetime
from zope.app.dublincore.interfaces import IZopeDublinCore

def ModifiedAnnotator(event):
    dc = IZopeDublinCore(event.object, None)
    if dc is not None:
        dc.modified = datetime.utcnow()

def CreatedAnnotator(event):
    dc = IZopeDublinCore(event.object, None)
    if dc is not None:
        now = datetime.utcnow()
        dc.created = now
        dc.modified = now
