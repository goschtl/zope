##############################################################################
#
# Copyright (c) Zope Corporation and Contributors.
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

import zope.component
import zope.interface
import zope.app.publisher.browser.directoryresource

class DirectoryResource(
    zope.app.publisher.browser.directoryresource.DirectoryResource):

    def publishTraverse(self, request, name):
        if name == 'set_blank_image.js':
            return self.set_blank_image_js
        return self.get(name)

    def set_blank_image_js(self):
        extjs = zope.component.getAdapter(
            self.request, zope.interface.Interface, 'extjs')
        return (
            "Ext.BLANK_IMAGE_URL = '%s/resources/images/default/s.gif';\n"
            % extjs()
            )

class DirectoryResourceFactory(
    zope.app.publisher.browser.directoryresource.DirectoryResourceFactory):

    def __init__(self, path, checker, name):
        self.__dir = zope.app.publisher.browser.directoryresource.Directory(
            path, checker, name)
        self.__checker = checker
        self.__name = name
    
    def __call__(self, request):
        resource = DirectoryResource(self.__dir, request)
        resource.__Security_checker__ = self.__checker
        resource.__name__ = self.__name
        return resource
