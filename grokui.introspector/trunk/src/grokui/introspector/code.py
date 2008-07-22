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
"""Introspecting code.
"""
import grok
from grokcore.component.interfaces import IContext
import types
from martian.scan import module_info_from_dotted_name
from martian.util import isclass

class Code(object):
    grok.implements(IContext)

    def __init__(self, dotted_name):
        self.dotted_name = dotted_name

class Index(grok.View):
    grok.context(Code)
    def render(self):
        return "This is code"

class PackageOrModule(Code):
    def __init__(self, dotted_name):
        super(PackageOrModule, self).__init__(dotted_name)
        self._module_info = module_info_from_dotted_name(dotted_name)
    
class Package(PackageOrModule):    
    def traverse(self, name):
        sub_module = self._module_info.getSubModuleInfo(name)
        if sub_module is None:
            return None
        if sub_module.isPackage():
            return Package(sub_module.dotted_name)
        return Module(sub_module.dotted_name)

class Module(PackageOrModule):
    def traverse(self, name):
        module = self._module_info.getModule()
        obj = getattr(module, name, None)
        if obj is None:
            return None
        sub_dotted_name = self.dotted_name + '.' + name
        if isclass(obj):
            return Class(sub_dotted_name)
        elif type(obj) is types.FunctionType:
            return Function(sub_dotted_name)
        else:
            return Instance(sub_dotted_name)


class Class(Code):
    pass

class Function(Code):
    pass

class Instance(Code):
    pass
