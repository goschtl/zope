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

$Id: ZPTTemplateAdd.py,v 1.1 2002/12/23 08:15:39 srichter Exp $
"""
from Zope.Publisher.VFS.VFSView import VFSView

from Zope.Event import publish
from Zope.App.Event.ObjectEvent import ObjectCreatedEvent

from Zope.App.OFS.Services.ServiceManager.IPackageAdding import IPackageAdding
from Zope.App.OFS.Services.zpt import ZPTTemplate


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

