##############################################################################
#
# Copyright (c) 2003, 2004 Zope Corporation and Contributors.
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
"""Case-Insensitive Traverser and Folder

$Id: __init__.py 26729 2004-07-23 21:20:21Z pruggera $
"""
__docformat__ = 'restructuredtext'
from zope.component.interfaces import IFactory
from zope.interface import implements, implementedBy
from zope.interface import directlyProvides, directlyProvidedBy 
from zope.publisher.interfaces import NotFound

from zope.app import zapi
from zope.app.folder import Folder
from zope.app.folder.interfaces import IFolder
from zope.app.container.traversal import ContainerTraverser


class ICaseInsensitiveFolder(IFolder):
    """Marker for folders whose contained items keys are case insensitive.

    When traversing in this folder, all names will be converted to lower
    case. For example, if the traverser requests an item called 'Foo', in
    reality the first item matching 'foo' or any upper-and-lowercase variants
    are looked up in the container."""

class CaseInsensitiveFolderFactory(object):
    """A Factory that creates case-insensitive Folders."""
    implements(IFactory)

    title = "Case-Insensitive Folder Factory"
    description = "A Factory that creates case-insensitive Folders."

    def __call__(self):
        """See zope.component.interfaces.IFactory

        Create a folder and mark it as case insensitive.
        """
        folder = Folder()
        directlyProvides(folder, directlyProvidedBy(folder),
                         ICaseInsensitiveFolder)
        return folder
    
    def getInterfaces(self):
        """See zope.component.interfaces.IFactory"""
        return implementedBy(Folder) + ICaseInsensitiveFolder

caseInsensitiveFolderFactory = CaseInsensitiveFolderFactory()


class CaseInsensitiveFolderTraverser(ContainerTraverser):

    __used_for__ = ICaseInsensitiveFolder

    def publishTraverse(self, request, name):
        """See zope.publisher.interfaces.browser.IBrowserPublisher"""
        subob = self._guessTraverse(name) 
        if subob is None:
            view = zapi.queryView(self.context, name, request)
            if view is not None:
                return view

            raise NotFound(self.context, name, request)
         
        return subob

    def _guessTraverse(self, name):
        for key in self.context.keys():
            if key.lower() == name.lower():
                return self.context[key]
        return None
