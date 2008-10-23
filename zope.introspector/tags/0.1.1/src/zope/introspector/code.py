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

import inspect
import types
import pkg_resources
import grokcore.component as grok
from pkg_resources import DistributionNotFound
from grokcore.component.interfaces import IContext
from martian.scan import module_info_from_dotted_name
from martian.util import isclass
from zope.interface import implements, implementedBy
from zope.introspector.interfaces import IInfo, IDocString
from zope.introspector.util import (resolve, get_package_items,
                                    is_namespace_package, get_attributes,
                                    get_function_signature,
                                    get_interface_for_attribute)
import os

class Code(object):
    implements(IContext)

    def __init__(self, dotted_name):
        self.dotted_name = dotted_name

class PackageOrModule(Code):
    def __init__(self, dotted_name):
        super(PackageOrModule, self).__init__(dotted_name)
        self._module_info = module_info_from_dotted_name(dotted_name)
        self._module = self._module_info.getModule()

    def getModuleInfo(self):
        return self._module_info

class Package(PackageOrModule):
    def getPath(self):
        return os.path.dirname(self._module_info.path)

    def __getitem__(self, name):
        sub_module = None
        try:
            sub_module = module_info_from_dotted_name(
                self.dotted_name + '.' + name)
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
            except AttributeError:
                # This is thrown sometimes by martian.scan if an
                # object lacks a __file__ attribute and needs further
                # investigation.
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

class ModuleInfo(grok.Adapter):
    grok.context(Module)
    grok.provides(IInfo)
    grok.name('module')

    def getDottedName(self):
        return self.context.dotted_name

    def getPath(self):
        return self.context.getPath()

    def _standardFilter(self, item):
        """Filter out, what we don't consider a module item.
        """
        if getattr(item, '__module__', None) != self.context._module.__name__:
            return False
        return hasattr(item, '__name__')

    def getMembers(self, filter_func=lambda x:True):
        members = inspect.getmembers(
            self.context._module,
            predicate=lambda x: filter_func(x) and self._standardFilter(x))
        return [self.context[x[0]] for x in members]
        
    def getClasses(self):
        return self.getMembers(filter_func=isclass)

    def getFunctions(self):
        filter_func = lambda x: inspect.isfunction(x) or inspect.ismethod(x)
        return self.getMembers(filter_func=filter_func)
        

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

    def __init__(self, dotted_name):
        super(Class, self).__init__(dotted_name)
        self._klass = resolve(dotted_name)
        # Setup interfaces that are implemented by this class.
        self._interfaces = tuple(implementedBy(self._klass))
        all_ifaces = {}
        self._all_ifaces = tuple(implementedBy(self._klass).flattened())

class ClassInfo(grok.Adapter):
    grok.context(Class)
    grok.provides(IInfo)
    grok.name('class')

    def _iterAllAttributes(self):
        for name in get_attributes(self.context._klass):
            iface = get_interface_for_attribute(
                    name, self.context._all_ifaces, as_path=False)
            yield name, getattr(self.context._klass, name), iface

    def getBases(self):
        return (Class('%s.%s' % (x.__module__, x.__name__))
                for x in self.context._klass.__bases__)

    def getInterfaces(self):
        return self.context._interfaces

    def getAttributes(self):
        return [(name, obj, iface)
                for name, obj, iface in self._iterAllAttributes()
                if not (inspect.ismethod(obj)
                        or inspect.ismethoddescriptor(obj))]

    def getMethods(self):
        return [(name, obj, iface)
                for name, obj, iface in self._iterAllAttributes()
                if inspect.ismethod(obj)]

    def getMethodDescriptors(self):
        return [(name, obj, iface)
                for name, obj, iface in self._iterAllAttributes()
                if inspect.ismethoddescriptor(obj)]


class Function(Code):

    def __init__(self, dotted_name):
        super(Function, self).__init__(dotted_name)
        self.func = resolve(self.dotted_name)

    def getSignature(self):
        return get_function_signature(self.func)

class FunctionInfo(grok.Adapter):
    grok.context(Function)
    grok.provides(IInfo)
    grok.name('function')

    def getSignature(self):
        return self.context.getSignature()

class Instance(Code):
    pass


class DocString(grok.Adapter):
    grok.context(Code)
    grok.provides(IDocString)

    def getDocString(self, heading_only=True):
        try:
            obj = resolve(self.context.dotted_name)
        except ImportError:
            return u''
        except AttributeError:
            return u''
        docstring = getattr(obj, '__doc__', None)
        if docstring is None:
            return u''
        lines = docstring.strip().split('\n')
        if len(lines) and heading_only:
            # Find first empty line to separate heading from trailing text.
            headlines = []
            for line in lines:
                if line.strip() == "":
                    break
                headlines.append(line)
            lines = headlines
        # Get rid of possible CVS id.
        lines = [line for line in lines if not line.startswith('$Id')]
        return '\n'.join(lines)
