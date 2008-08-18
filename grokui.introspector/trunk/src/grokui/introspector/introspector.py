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
"""A traverser and other other central stuff for introspecting.
"""
import grok
from zope.component import getUtility
from zope.introspector.interfaces import IRegistryInfo
from grokui.introspector.interfaces import (IGrokRegistryIntrospector,
                                            IGrokCodeIntrospector,
                                            IGrokContentIntrospector)
from zope.app.folder.interfaces import IRootFolder
from zope.introspector.code import Package

class RootTraverser(grok.Traverser):
    grok.context(IRootFolder)

    def traverse(self, name): 
        if name == '+code':
            return CodeIntrospector()
        elif name == '+registry':
            return RegistryIntrospector()
        elif name == '+content':
            return ContentIntrospector()
        return None
    
class RegistryIntrospector(grok.Model):
    grok.implements(IGrokRegistryIntrospector)

    def getUtilities(self):
        uinfo = getUtility(IRegistryInfo)
        utilities = [dict(
            component = x.component,
            name = x.name,
            provided = x.provided,
            registry = x.registry
            ) for x in uinfo.getAllUtilities()]
        return utilities

class CodeIntrospector(grok.Model):
    grok.implements(IGrokCodeIntrospector)

    def traverse(self, name):
        if '.' in name:
            return None
        try:
            return Package(name)
        except ImportError:
            return None

class ContentIntrospector(grok.Model):
    grok.implements(IGrokContentIntrospector)
