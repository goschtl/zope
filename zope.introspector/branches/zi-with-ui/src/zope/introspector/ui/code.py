##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
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
import grokcore.view as grok

from zope.location.location import located

from zope.introspector.code import PackageInfo

class Package(grok.View):
    grok.context(PackageInfo)
    grok.name('index')

    def update(self):
        self.files = self.getTextFileUrls()

    def getTextFileUrls(self):
        filenames = self.context.getPackageFiles()
        result = []
        package = self.context.context
        for name in filenames:
            file = located(package[name], package, name)
            result.append(dict(name=name, url=self.url(file)))
        return result
