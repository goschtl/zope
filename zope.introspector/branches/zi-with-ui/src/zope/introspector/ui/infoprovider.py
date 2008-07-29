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
from grokcore.view import View
from grokcore.component import context, name
from zope.introspector.interfaces import (IObjectInfo, IModuleInfo,
                                          IPackageInfo, IViewInfo)

class Object(View):
    name('index.html')
    context(IObjectInfo)
        
    def getType(self):
        return self.context.getType().__name__

class Module(Object):
    context(IModuleInfo)
    name('index.html')

class Package(Object):
    context(IPackageInfo)
    name('index.html')

    def update(self, *args, **kw):
        super(Package, self).update(*args, **kw)
        self.files = self.getPackageFiles()

    def getPackageFiles(self, filter=None):
        files = self.context.getPackageFiles(filter=filter)
        result = []
        for name in files:
            dotnum = name.count('.')
            url = self.context.getDottedName() + '.' + name
            url = url.split('.', dotnum*2)[-1]
            result.append(dict(name=name, url=url))
        return result

class View(View):
    name('index.html')
    context(IViewInfo)
