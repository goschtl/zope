##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""

Revision information: $Id: package.py,v 1.2 2002/12/25 14:12:36 jim Exp $
"""
from zope.app.browser.container.contents import Contents
from zope.app.interfaces.services.service import IServiceManager
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.app.services.package import Package
from zope.app.services.zpt import ZPTTemplate


class ViewPackageContents(Contents):

    __used_for__ = IServiceManager

    index = ViewPageTemplateFile('viewpackage_contents.pt')

    def add(self, name):
        self.context.setObject(name, ZPTTemplate())
        self.request.response.redirect('.')


class PackagesContents(Contents):

    __used_for__ = IServiceManager

    index = ViewPageTemplateFile('packages_contents.pt')

    def addPackage(self, name):
        self.context.setObject(name, Package())
        self.request.response.redirect('.')
