##############################################################################
#
# Copyright (c) 2003, 2004 Zope Corporation and Contributors.
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
"""Case-Insensitive Traverser and Folder

$Id: __init__.py,v 1.1 2004/02/13 23:28:45 srichter Exp $
"""
from zope.app import zapi
from zope.app.content.folder import Folder
from zope.app.interfaces.container import ISimpleReadContainer
from zope.component.interfaces import IFactory
from zope.interface import implements, directlyProvides, directlyProvidedBy
from zope.interface import implementedBy
from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces.browser import IBrowserPublisher
from interfaces import \
     ICaseInsensitiveFolder, ICaseInsensitiveContainerTraverser

class CaseInsensitiveContainerTraverser(object):

    implements(IBrowserPublisher, ICaseInsensitiveContainerTraverser)
    __used_for__ = ISimpleReadContainer

    def __init__(self, container, request):
        """Initialize object."""
        self.context = container
        self.request = request

    def publishTraverse(self, request, name):
        """See zope.publisher.interfaces.browser.IBrowserPublisher"""
        subob = self.context.get(name, None)
        if subob is None:
            view = zapi.queryView(self.context, name, request)
            if view is not None:
                return view

            subob = self.guessTraverse(name) 
            if subob is None:
                raise NotFound(self.context, name, request)
         
        return subob

    def guessTraverse(self, name):
        """See friendlyfolder.interfaces.IFriendlyContainerTraverser"""
        for key in self.context.keys():
            if key.lower() == name.lower():
                return self.context[key]
        return None

    def browserDefault(self, request):
        """See zope.publisher.interfaces.browser.IBrowserPublisher"""
        view_name = zapi.getDefaultViewName(self.context, request)
        view_uri = "@@%s" % view_name
        return self.context, (view_uri,)


class CaseInsensitiveFolderFactory(object):
    """A Factory that creates case-insensitive Folders."""
    implements(IFactory)

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
