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
    
from zope.introspector.code import (PackageInfo, FileInfo, ModuleInfo,
                                    ClassInfo, Function)
from zope.introspector.interfaces import IDocString
from zope.introspector.util import get_function_signature
from zope.introspectorui.interfaces import IBreadcrumbProvider, ICodeView

class Module(grok.View):
    grok.implements(ICodeView)
    grok.context(ModuleInfo)
    grok.name('index')

    def update(self):
        self.docstring = self.getDocString(heading_only=False)
        self.classes = self.getClassURLs()
        self.functions = self.getFunctions()

    def getDocString(self, item=None, heading_only=True):
        if item is None:
            item = self.context.context
        return IDocString(item).getDocString(heading_only=heading_only)

    def getItemURLs(self, items):
        module = self.context.context
        result = []
        for item in items:
            name = item.dotted_name.split('.')[-1]
            obj = located(module[name], module, name)
            result.append(dict(name=name, url=self.url(obj),
                               doc=self.getDocString(obj)))
        return sorted(result, key=lambda x: x['name'])

    def getClassURLs(self):
        classes = self.context.getClasses()
        return self.getItemURLs(classes)

    def getFunctionURLs(self):
        functions = self.context.getFunctions()
        return self.getItemURLs(functions)

    def getFunctions(self):
        functions = self.context.getFunctions()
        result = []
        for func in functions:
            name = func.dotted_name.split('.')[-1]
            signature = func.getSignature()
            result.append(dict(name=name,
                               signature=signature,
                               fullname=name+signature,
                               doc=self.getDocString(func,
                                                     heading_only=False)))
        return sorted(result, key=lambda x: x['fullname'])

    def getBreadcrumbs(self):
        return IBreadcrumbProvider(self).getBreadcrumbs()


class Package(grok.View):
    grok.implements(ICodeView)
    grok.context(PackageInfo)
    grok.name('index')

    def update(self):
        self.docstring = self.getDocString(heading_only=False)
        self.files = self.getTextFileUrls()
        self.zcmlfiles = self.getZCMLFileUrls()
        self.subpkgs = self.getSubPackageUrls()
        self.modules = self.getModuleUrls()

    def getDocString(self, item=None, heading_only=True):
        if item is None:
            item = self.context.context
        return IDocString(item).getDocString(heading_only=heading_only)

    def _getFileUrls(self, filenames):
        result = []
        package = self.context.context
        for name in filenames:
            file = located(package[name], package, name)
            result.append(dict(name=name, url=self.url(file)))
        return sorted(result, key=lambda x: x['name'])

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
                               doc=self.getDocString(item=mod)))
        return sorted(result, key=lambda x: x['name'])
        
    def getSubPackageUrls(self):
        mod_infos = self.context.getSubPackages()
        return self._getItemUrls(mod_infos)

    def getModuleUrls(self):
        mod_infos = self.context.getModules()
        return self._getItemUrls(mod_infos)

    def getBreadcrumbs(self):
        return IBreadcrumbProvider(self).getBreadcrumbs()

class Class(grok.View):
    grok.implements(ICodeView)
    grok.context(ClassInfo)
    grok.name('index')

    def update(self):
        self.docstring = self.getDocString(heading_only=False)
        self.bases = self.getBases()
        self.attributes = self.getAttributes()
        self.methods = self.getMethods()

    def getDocString(self, item=None, heading_only=True):
        if item is None:
            item = self.context.context
        return IDocString(item).getDocString(heading_only=heading_only)

    def _locate(self, obj):
        from zope.introspector.code import Package
        root = self.context.context
        while not isinstance(root, Package) or isinstance(
            root.__parent__, Package):
            root = root.__parent__
        top_pkg_name = obj.dotted_name.split('.')[0]
        result = located(Package(top_pkg_name),
                           root.__parent__,
                           top_pkg_name)
        for part in obj.dotted_name.split('.')[1:]:
            result = located(result[part], result, part)
        return result
        

    def getBases(self):
        bases = list(self.context.getBases())
        result = []
        for base in bases:
            url = None
            try:
                url = self.url(self._locate(base))
            except AttributeError:
                # martian.scan cannot handle builtins
                continue
            result.append(dict(name=base.dotted_name,
                               url=url,
                               doc=self.getDocString(item=base)))
        return result
        return (dict(name=x.dotted_name,
                     url=self.url(self._locate(x)),
                     doc=self.getDocString(item=x))
                for x in bases)

    def getAttributes(self):
        return sorted([x[0] for x in self.context.getAttributes()])

    def getMethods(self):
        result = []
        for name, obj, iface in self.context.getMethods():
            dotted_name = self.context.context.dotted_name + '.' + name
            item = Function(dotted_name)
            signature = get_function_signature(obj)
            if signature == '()':
                signature = '(self)'
            else:
                signature = '(self, ' + signature[1:]
            result.append(dict(name=name + signature,
                               doc=self.getDocString(item=item)))
        return sorted(result, key=lambda x: x['name'])

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
