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
"""VFS ZPTTemplate Add View

$Id: zpt.py,v 1.2 2002/12/25 14:13:30 jim Exp $
"""
from zope.publisher.vfs import VFSView

from zope.event import publish
from zope.app.event.objectevent import ObjectCreatedEvent

from zope.app.interfaces.services.package import IPackageAdding
from zope.app.services.zpt import ZPTTemplate


class ZPTTemplateAdd(VFSView):
    "Provide a user interface for adding a ZPTTemplate content object"

    __used_for__ = IPackageAdding

    def __call__(self, mode, instream, start):
        content = ZPTTemplate()
        try:
            instream.seek(start)
        except:
            pass
        content.source = unicode(instream.read())

        publish(self.context, ObjectCreatedEvent(content))
        return self.context.add(content)



"""VFS-View for IZPTTemplate

VFS-view implementation for a ZPT Template.

$Id: zpt.py,v 1.2 2002/12/25 14:13:30 jim Exp $
"""
from zope.publisher.vfs import VFSFileView

class ZPTTemplateView(VFSFileView):

    def _setData(self, data):
        self.context.source = data

    def _getData(self):
        return self.context.source
