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
"""VFS Package Add View

$Id: PackageAdd.py,v 1.1 2002/12/23 08:15:38 srichter Exp $
"""
from Zope.Publisher.VFS.VFSView import VFSView

from Zope.Event import publish
from Zope.App.Event.ObjectEvent import ObjectCreatedEvent

from Zope.App.OFS.Container.IAdding import IAdding
from Zope.App.OFS.Services.ServiceManager.Package import Package


class PackageAdd(VFSView):
    "Provide a user interface for adding a Package content object"

    __used_for__ = IAdding

    def __call__(self):
        "Add a folder"
        content = Package()
        publish(self.context, ObjectCreatedEvent(content))
        return self.context.add(content)

