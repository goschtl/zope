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
"""The real information providers for code objects (packages, classes, etc.)
"""

import pkg_resources
from pkg_resources import DistributionNotFound
import grokcore.component as grok
from grokcore.component.interfaces import IContext
import types
from martian.scan import module_info_from_dotted_name
from martian.util import isclass
from zope.interface import implements
from zope.introspector.interfaces import IInfo
from zope.introspector.util import (resolve, get_package_items,
                                    is_namespace_package)
import os

class Code(object):
    implements(IContext)

    def __init__(self, dotted_name):
        self.dotted_name = dotted_name

class PackageOrModule(Code):
    def __init__(self, dotted_name):
        super(PackageOrModule, self).__init__(dotted_name)
        self._module_info = module_info_from_dotted_name(dotted_name)

    def getModuleInfo(self):
        return self._module_info
    
class Package(PackageOrModule):
    def getPath(self):
        return os.path.dirname(self._module_info.path)

    def __getitem__(self, name):
        sub_module = None
        try:
            sub_module = module_info_from_dotted_name(
                self._module_info.dotted_name + '.' + name)
        except ImportError:
            # No module of that name found. The name might denote
            # something different like a file or be really trash.
            pass
        if sub_module is None:
            file = File(self.dotted_name, name)
            # if the file exists, use it, otherwise it's a KeyError - no
            # file is here
            if file.exists():
                return file
            else:
                raise KeyError
        if sub_module.isPackage():
            return Package(sub_module.dotted_name)
        return Module(sub_module.dotted_name)

class PackageInfo(grok.Adapter):
    grok.context(Package)
    grok.provides(IInfo)
    grok.name('package')

    def isNamespacePackage(self):
        return is_namespace_package(self.context.dotted_name)

    def getDottedName(self):
        return self.context.dotted_name

    def getPath(self):
        return self.context.getPath()

    def getPackageFiles(self):
        result = [x for x in get_package_items(self.context.dotted_name)
                  if '.' in x and x.rsplit('.', 1)[-1] in ['txt', 'rst']]
        return sorted(result)

    def getZCMLFiles(self):
        result = [x for x in get_package_items(self.context.dotted_name)
                  if '.' in x and x.rsplit('.', 1)[-1] in ['zcml']]
        return sorted(result)

    def _filterSubItems(self, filter=lambda x: True):
        for name in get_package_items(self.context.dotted_name):
            try:
                info = module_info_from_dotted_name(
                    self.context.dotted_name + '.' + name)
                if filter and filter(info):
                    yield info
            except ImportError:
                pass
        
    def getSubPackages(self):
        return sorted(self._filterSubItems(lambda x: x.isPackage()))

    def getModules(self):
        return sorted(self._filterSubItems(lambda x: not x.isPackage()))

    def getEggInfo(self):
        try:
            info = pkg_resources.get_distribution(self.context.dotted_name)
        except DistributionNotFound:
            return None
        version = info.has_version and info.version or None
        return dict(
            name=info.project_name,
            version=version,
            py_version=info.py_version,
            location=info.location)

class Module(PackageOrModule):

    def getPath(self):
        return self._module_info.path

    def __getitem__(self, name):
        module = self._module_info.getModule()
        obj = getattr(module, name, None)
        if obj is None:
            raise KeyError
        sub_dotted_name = self.dotted_name + '.' + name
        if isclass(obj):
            return Class(sub_dotted_name)
        elif type(obj) is types.FunctionType:
            return Function(sub_dotted_name)
        else:
            return Instance(sub_dotted_name)

class File(Code):
    def __init__(self, dotted_name, name):
        super(File, self).__init__(dotted_name)
        self.name = name
        module_info = module_info_from_dotted_name(self.dotted_name)
        self.path = module_info.getResourcePath(self.name)

    def exists(self):
        """Check whether the file is a file we want to consider."""
        return (os.path.isfile(self.path) and
                os.path.splitext(self.path)[1].lower() in [
                    '.rst', '.txt', '.zcml'])

class FileInfo(grok.Adapter):
    grok.context(File)
    grok.provides(IInfo)
    grok.name('file')

    def getDottedName(self):
        return self.context.dotted_name

    def getName(self):
        return self.context.name

    def getPath(self):
        return self.context.path


class Class(Code):
    pass

class Function(Code):
    pass

class Instance(Code):
    pass
