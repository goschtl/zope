##############################################################################
#
# Copyright (c) 2006-2007 Zope Corporation and Contributors.
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
"""Genshi components"""
import zope.interface
import grok.components
import grok.interfaces
import genshi.template
import grok
import martian

class GenshiTemplateBase(grok.components.GrokPageTemplate):
        
    def render(self, view):
        stream = self._template.generate(**self.namespace(view))
        return stream.render(self.result_type)


class GenshiMarkupTemplate(GenshiTemplateBase):
    
    result_type = 'xhtml'
    
    def __init__(self, html):
        self._template = genshi.template.MarkupTemplate(html)
        self.__grok_module__ = martian.util.caller_module()

        
class GenshiMarkupTemplateFile(GenshiTemplateBase, grok.components.GlobalUtility):

    zope.interface.implements(grok.interfaces.ITemplateFile)
    zope.interface.classProvides(grok.interfaces.ITemplateFileFactory)
    grok.name('g')
    grok.direct()

    result_type = 'xhtml'

    def __init__(self, filename, _prefix=None):
        loader = genshi.template.TemplateLoader(_prefix)
        self._template = loader.load(filename)
        self.__grok_module__ = martian.util.caller_module()


class GenshiTextTemplateFile(GenshiTemplateBase, grok.components.GlobalUtility):

    result_type = 'xhtml'
    
    zope.interface.implements(grok.interfaces.ITemplateFile)
    zope.interface.classProvides(grok.interfaces.ITemplateFileFactory)
    grok.name('gt')
    grok.direct()
    
    def __init__(self, filename, _prefix=None):
        loader = genshi.template.TemplateLoader(_prefix)
        self._template = loader.load(filename, cls=genshi.template.TextTemplate)
        self.__grok_module__ = martian.util.caller_module()
