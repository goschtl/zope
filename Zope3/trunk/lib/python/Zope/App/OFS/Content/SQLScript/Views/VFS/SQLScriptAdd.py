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
"""VFS SQLScript Add View

$Id: SQLScriptAdd.py,v 1.1 2002/12/20 10:31:48 srichter Exp $
"""
from Zope.Publisher.VFS.VFSView import VFSView

from Zope.Event import publish
from Zope.Event.ObjectEvent import ObjectCreatedEvent

from Zope.App.OFS.Container.IAdding import IAdding
from Zope.App.OFS.Content.SQLScript.SQLScript import SQLScript


class SQLScriptAdd(VFSView):
    "Provide a user interface for adding a SQLScript content object"

    __used_for__ = IAdding

    def __call__(self, mode, instream, start):
        content = SQLScript()
        try:
            instream.seek(start)
        except:
            pass
        content.setSource(instream.read())
        
        publish(self.context, ObjectCreatedEvent(content))
        return self.context.add(content)

