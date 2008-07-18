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
from zope.introspector.interfaces import (IRegistryInfo,
                                          IObjectDescriptionProvider,)
from zope.location.interfaces import ILocation
from zope.traversing.interfaces import ITraversable
from grok.interfaces import IContext
from grokui.introspector.interfaces import (IGrokIntrospector,
                                            IGrokRegistryIntrospector,
                                            IGrokCodeIntrospector,
                                            IGrokZODBBrowser)

class Introspector(object):
    grok.implements(IGrokIntrospector, ILocation, IContext)

    def __init__(self, parent, name):
        self.__parent__ = parent
        self.__name__ = name

def get_introspector():
    return Introspector
grok.global_utility(get_introspector, provides=IGrokIntrospector)

class IntrospectorTraverser(grok.Traverser):
    grok.context(IGrokIntrospector)
    def traverse(self, path, *args, **kw):
        if path == 'registries':
            return RegistryIntrospector()
        if path == 'code':
            return CodeIntrospector()
        if path == 'zodb':
            return ZODBBrowser()
        return self.context

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
    
    def __init__(self, dotted_name=None, *args, **kw):
        super(CodeIntrospector, self).__init__(*args, **kw)
        self.dotted_name = dotted_name

    def getIntrospector(self):
        if self.dotted_name is None:
            return self
        provider = getUtility(IObjectDescriptionProvider)
        description = provider.getDescription(dotted_name=self.dotted_name)
        return description

class CodeTraverser(grok.Traverser):
    grok.context(IGrokCodeIntrospector)

    def traverse(self, path, *args, **kw):
        dotted_name = self.context.dotted_name or ''
        if len(dotted_name):
            dotted_name += '.'
        dotted_name += path
        introspector = CodeIntrospector(dotted_name=dotted_name)
        return introspector.getIntrospector()

class ZODBBrowser(grok.Model):
    grok.implements(IGrokZODBBrowser)
