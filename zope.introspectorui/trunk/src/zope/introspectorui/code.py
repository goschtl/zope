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
"""Views for code-related infos.
"""
import grokcore.view as grok
try:
    from zope.location.location import located
except ImportError:
    # Zope 2.10 compatibility:
    from zope.location.interfaces import ILocation
    from zope.location.location import LocationProxy, locate
    def located(object, parent, name=None):
        """Locate an object in another and return it.
    
        If the object does not provide ILocation a LocationProxy is returned.
    
        """
        if ILocation.providedBy(object):
            if parent is not object.__parent__ or name != object.__name__:
                locate(object, parent, name)
            return object
        return LocationProxy(object, parent, name)
    
from zope.introspector.code import PackageInfo, FileInfo, ModuleInfo
from zope.introspectorui.interfaces import IBreadcrumbProvider, ICodeView

class Module(grok.View):
    grok.implements(ICodeView)
    grok.context(ModuleInfo)
    grok.name('index')

    def update(self):
        self.classes = self.getClassURLs()
        self.functions = self.getFunctions()

    def getDocString(self, item):
        if hasattr(item, 'getDocString'):
            return item.getDocString()
        return u''

    def getItemURLs(self, items):
        module = self.context.context
        result = []
        for item in items:
            name = item.dotted_name.split('.')[-1]
            obj = located(module[name], module, name)
            result.append(dict(name=name, url=self.url(obj),
                               doc=self.getDocString(obj)))
        return result

    def getClassURLs(self):
        classes = self.context.getClasses()
        return sorted(self.getItemURLs(classes))

    def getFunctionURLs(self):
        functions = self.context.getFunctions()
        return sorted(self.getItemURLs(functions))

    def getFunctions(self):
        functions = self.context.getFunctions()
        result = []
        for func in functions:
            name = func.dotted_name.split('.')[-1]
            signature = func.getSignature()
            result.append(dict(name=name,
                               signature=signature,
                               fullname=name+signature))
        return result

    def getBreadcrumbs(self):
        return IBreadcrumbProvider(self).getBreadcrumbs()


class Package(grok.View):
    grok.implements(ICodeView)
    grok.context(PackageInfo)
    grok.name('index')

    def update(self):
        self.files = self.getTextFileUrls()
        self.zcmlfiles = self.getZCMLFileUrls()
        self.subpkgs = self.getSubPackageUrls()
        self.modules = self.getModuleUrls()

    def getDocString(self, item):
        if hasattr(item, 'getDocString'):
            return item.getDocString()
        return u''

    def _getFileUrls(self, filenames):
        result = []
        package = self.context.context
        for name in filenames:
            file = located(package[name], package, name)
            result.append(dict(name=name, url=self.url(file)))
        return sorted(result)

    def getTextFileUrls(self):
        filenames = self.context.getPackageFiles()
        return self._getFileUrls(filenames)

    def getZCMLFileUrls(self):
        filenames = self.context.getZCMLFiles()
        return self._getFileUrls(filenames)

    def _getItemUrls(self, mod_infos):
        result = []
        package = self.context.context
        for info in mod_infos:
            mod = located(package[info.name], package, info.name)
            result.append(dict(name=info.name, url=self.url(mod),
                               doc=self.getDocString(mod)))
        return result
        
    def getSubPackageUrls(self):
        mod_infos = self.context.getSubPackages()
        return sorted(self._getItemUrls(mod_infos))

    def getModuleUrls(self):
        mod_infos = self.context.getModules()
        return sorted(self._getItemUrls(mod_infos))

    def getBreadcrumbs(self):
        return IBreadcrumbProvider(self).getBreadcrumbs()

class File(grok.View):
    grok.implements(ICodeView)
    grok.context(FileInfo)
    grok.name('index')

    def getBreadcrumbs(self):
        return IBreadcrumbProvider(self).getBreadcrumbs()

    def getRaw(self):
        return open(self.context.getPath(), 'r').read()
