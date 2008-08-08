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
"""Representations of simple objects.
"""
import os
import inspect
import types
import grokcore.component as grok
from zope.interface import Interface
from zope.introspector.interfaces import (IObjectInfo, IModuleInfo,
                                          IPackageInfo, ITypeInfo)

class ObjectInfo(grok.Adapter):
    grok.implements(IObjectInfo)
    grok.context(Interface)
    grok.name('object')
    
    dotted_name = None
    
    def __init__(self, obj):
        self.obj = obj
        
    def getType(self):
        return type(self.obj)
    
    def isModule(self):
        return inspect.ismodule(self.obj)

    def isClass(self):
        return inspect.isclass(self.obj)
    
    def getDottedName(self):
        if self.isClass():
            class_ = self.obj
        else:
            class_ = self.obj.__class__
            
        return class_.__module__ + '.' + class_.__name__
    
    def getFile(self):
        try:
            return inspect.getsourcefile(self.obj.__class__)
        except TypeError:
            try:
                return inspect.getsourcefile(self.getType())
            except TypeError:
                # This is probably a built-in or dynamically created type
                return 'builtin'
        
    def getAttributes(self):
        attributes = []
        for id, value in inspect.getmembers(self.obj.__class__):
            if inspect.ismethod(value):
                continue
            attributes.append({'id': id,
                               'value': value,
                               })
        return attributes
            
    def getMethods(self):
        methods = []
        for id, value in inspect.getmembers(self.obj.__class__):
            if inspect.ismethod(value):
                try:
                    methods.append({'id': id,
                                    'args':inspect.getargspec(value),
                                    'comment': inspect.getcomments(value),
                                    'doc': inspect.getdoc(value),
                                    })
                except:
                    pass
                    
        return methods

class ModuleInfo(ObjectInfo):
    grok.implements(IModuleInfo)
    grok.provides(IObjectInfo)
    grok.context(types.ModuleType)
    grok.name('module')
    
    def getDottedName(self):
        return self.obj.__name__

class PackageInfo(ModuleInfo):
    grok.implements(IPackageInfo)
    grok.provides(IPackageInfo)
    grok.name('package')
    
    def getPackageFiles(self, filter=None):
        pkg_file_path = os.path.dirname(self.obj.__file__)
        return sorted([x for x in os.listdir(pkg_file_path)
               if os.path.isfile(os.path.join(pkg_file_path, x))
               and (x.endswith('.txt') or x.endswith('.rst'))])

class TypeInfo(ObjectInfo):
    grok.implements(ITypeInfo)
    grok.provides(IObjectInfo)
    grok.context(types.TypeType)
    grok.name('type')
