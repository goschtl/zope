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
"""Dublin Core Meta Data View

$Id$
"""
from datetime import datetime
from zope.event import notify
from zope.app.event.objectevent import ObjectAnnotationsModifiedEvent
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.dublincore.interfaces import IZopeDublinCore

__metaclass__ = type

class MetaDataEdit:
    """Provide view for editing basic dublin-core meta-data."""

    def edit(self):
        request = self.request
        formatter = self.request.locale.dates.getFormatter('dateTime', 'medium')
        dc = IZopeDublinCore(self.context)
        message=''

        if 'dctitle' in request:
            dc.title = request['dctitle']
            dc.description = request['dcdescription']
            notify(ObjectAnnotationsModifiedEvent(self.context))
            message = _("Changed data ${datetime}")
            message.mapping = {'datetime': formatter.format(datetime.utcnow())}

        return {
            'message': message,
            'dctitle': dc.title,
            'dcdescription': dc.description,
            'modified': (dc.modified or dc.created) and \
                        formatter.format(dc.modified or dc.created) or '',
            'created': dc.created and formatter.format(dc.created) or '',
            'creators': dc.creators
            }
