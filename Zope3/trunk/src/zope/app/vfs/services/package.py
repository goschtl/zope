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

$Id: package.py,v 1.3 2002/12/30 14:03:21 stevea Exp $
"""
from zope.publisher.vfs import VFSView

from zope.app.event import publish
from zope.app.event.objectevent import ObjectCreatedEvent

from zope.app.interfaces.container import IAdding
from zope.app.services.package import Package


class PackageAdd(VFSView):
    "Provide a user interface for adding a Package content object"

    __used_for__ = IAdding

    def __call__(self):
        "Add a folder"
        content = Package()
        publish(self.context, ObjectCreatedEvent(content))
        return self.context.add(content)



"""Adding View for IPackage

$Id: package.py,v 1.3 2002/12/30 14:03:21 stevea Exp $
"""
from zope.publisher.vfs import VFSView
from zope.app.vfs.container.adding import Adding
from zope.app.interfaces.services.package import IPackageAdding

class PackageAdding(Adding):

    __implements__ =  IPackageAdding, VFSView.__implements__


"""VFS-View for IPackages

$Id: package.py,v 1.3 2002/12/30 14:03:21 stevea Exp $
"""
import datetime
zerotime = datetime.datetime.fromtimestamp(0)

from zope.component import getAdapter
from zope.app.interfaces.dublincore import IZopeDublinCore
from zope.app.vfs.container.view import \
     VFSContainerView

class PackagesView(VFSContainerView):
    """Specific Packages VFS view."""

    __implments__ = VFSContainerView.__implements__

    _directory_type = 'Package'

    def remove(self, name):
        'See IVFSDirectoryPublisher'
        pass # not applicable

    def writefile(self, name, mode, instream, start=0):
        'See IVFSDirectoryPublisher'
        pass # not applicable




"""VFS-View for IPackage

$Id: package.py,v 1.3 2002/12/30 14:03:21 stevea Exp $
"""
import datetime
zerotime = datetime.datetime.fromtimestamp(0)

from zope.component import getAdapter
from zope.app.interfaces.dublincore import IZopeDublinCore
from zope.app.vfs.container.view import \
     VFSContainerView

class PackageView(VFSContainerView):
    """Specific Package VFS view."""

    __implments__ = VFSContainerView.__implements__

    _directory_type = 'Package'
