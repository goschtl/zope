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
"""VFS DTMLPage Add View

$Id: DTMLPageAdd.py,v 1.2 2002/12/21 15:32:49 poster Exp $
"""
from Zope.Publisher.VFS.VFSView import VFSView

from Zope.Event import publish
from Zope.App.Event.ObjectEvent import ObjectCreatedEvent

from Zope.App.OFS.Container.IAdding import IAdding
from Zope.App.OFS.Content.DTMLPage.DTMLPage import DTMLPage


class DTMLPageAdd(VFSView):
    "Provide a user interface for adding a DTMLPage content object"

    __used_for__ = IAdding

    def __call__(self, mode, instream, start):
        content = DTMLPage()
        try:
            instream.seek(start)
        except:
            pass
        content.setSource(instream.read())
        
        publish(self.context, ObjectCreatedEvent(content))
        return self.context.add(content)

