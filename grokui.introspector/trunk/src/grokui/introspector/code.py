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
from zope.introspector.code import Code, PackageOrModule
from zope.introspector.code import PackageInfo, FileInfo, ModuleInfo
from zope.introspectorui.code import Package, File, Module
from grokui.introspector.namespace import IntrospectorLayer
from grokui.introspector.util import get_url_with_namespaces, render_text

class CodeTraverser(grok.Traverser):
    grok.context(PackageOrModule)

    def traverse(self, name):
        try:
            return self.context[name]
        except KeyError:
            return None


class GrokUIPackage(Package):
    grok.context(PackageInfo)
    grok.name('index')
    grok.layer(IntrospectorLayer)

    def url(self, *args, **kw):
        result = super(GrokUIPackage, self).url(*args, **kw)
        result = get_url_with_namespaces(self.request, result)
        return result
        
    def render(self):
        # We have to provide a dummy renderer, that will not be used.
        return

class GrokUIModule(Module):
    grok.context(ModuleInfo)
    grok.name('index')
    grok.layer(IntrospectorLayer)

    def url(self, *args, **kw):
        result = super(GrokUIModule, self).url(*args, **kw)
        result = get_url_with_namespaces(self.request, result)
        return result

    def render(self):
        # We have to provide a dummy renderer, that will not be used.
        return

class GrokUIFile(File):
    grok.context(FileInfo)
    grok.name('index')
    grok.layer(IntrospectorLayer)
    grok.template('file')

    def url(self, *args, **kw):
        result = super(GrokUIFile, self).url(*args, **kw)
        result = get_url_with_namespaces(self.request, result)
        return result
        
    def getRenderedDoc(self):
        return render_text(self.getRaw())
