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
from zope.component import getUtility
from zope.introspector.interfaces import (IObjectInfo, IModuleInfo,
                                          IPackageInfo,
                                          IObjectDescriptionProvider,)
from zope.introspector.objectinfo import ObjectInfo
from grokui.introspector.interfaces import (IGrokIntrospector,)
from grokui.introspector.util import dotted_name_url

grok.context(IObjectInfo)

class Master(grok.View):
    """The Macro page that defines the default look and feel.
    """

class ObjectInfoView(grok.View):
    grok.name('index.html')

    def update(self, *args, **kw):
        self.dotted_name = dotted_name_url(self.context.getDottedName())
        
    def getType(self):
        return self.context.getType().__name__

class ModuleInfoView(ObjectInfoView):
    grok.context(IModuleInfo)
    grok.name('index.html')

class PackageInfoView(ObjectInfoView):
    grok.context(IPackageInfo)
    grok.name('index.html')

    def update(self, *args, **kw):
        super(PackageInfoView, self).update(*args, **kw)
        self.files = self.getPackageFiles()

    def getPackageFiles(self, filter=None):
        files = self.context.getPackageFiles(filter=filter)
        result = []
        for name in files:
            dotnum = name.count('.')
            url = dotted_name_url(self.context.getDottedName() + '.' + name,
                                  preserve_last = dotnum)
            url = url.split('.', dotnum*2)[-1]
            result.append(dict(name=name, url=url))
        return result

class DottedPathTraverser(grok.Traverser):
    """Traverse object infos.
    """
    def traverse(self, path, *args, **kw):
        dotted_name = '.'.join([self.context.getDottedName(), path])
        provider = getUtility(IObjectDescriptionProvider)
        try:
            description = provider.getDescription(dotted_name=dotted_name)
        except ImportError:
            # The required dotted name does not exist
            return CodeNotFound(dotted_name)
        return description

class CodeNotFound(object):
    """What we generate if a dotted name cannot be resolved.
    """
    grok.implements(IObjectInfo)
    def __init__(self, dotted_name):
        self.dotted_name = dotted_name

class CodeNotFoundView(grok.View):
    """The error view, when a dotted name cannot be resolved.
    """
    grok.context(CodeNotFound)
    grok.name('index.html')
    grok.template('codenotfound')
