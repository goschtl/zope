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
$Id: metadataedit.py,v 1.5 2003/08/02 08:46:24 anthony Exp $
"""

from zope.component import getAdapter
from zope.app.interfaces.dublincore import IZopeDublinCore
from datetime import datetime
from zope.app.event.objectevent import ObjectAnnotationsModifiedEvent
from zope.app.event import publish


__metaclass__ = type

class MetaDataEdit:
    """Provide view for editing basic dublin-core meta-data."""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def edit(self):
        request = self.request
        dc = getAdapter(self.context, IZopeDublinCore)
        message=''

        if 'dctitle' in request:
            dc.title = request['dctitle']
            dc.description = request['dcdescription']
            publish(self.context, ObjectAnnotationsModifiedEvent(self.context))
            message = "Changed data %s" % datetime.utcnow()

        return {
            'message': message,
            'dctitle': dc.title,
            'dcdescription': dc.description,
            'modified': dc.modified,
            'created': dc.created,
            'creators': dc.creators
            }

__doc__ = MetaDataEdit.__doc__ + __doc__
