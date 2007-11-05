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

class GenshiTemplateBase(grok.components.GrokTemplate):
        
    def render(self, view):
        stream = self._template.generate(**self.getNamespace(view))
        return stream.render(self.result_type)

    def fromTemplate(self, template):
        return self.cls(template)
        
    def fromFile(self, filename, _prefix=None):
        loader = genshi.template.TemplateLoader(_prefix)
        return loader.load(filename, cls=self.cls)

class GenshiMarkupTemplate(GenshiTemplateBase):
    
    result_type = 'xhtml'
    cls = genshi.template.MarkupTemplate
    
class GenshiTextTemplate(GenshiTemplateBase):

    result_type = 'text'
    cls = genshi.template.TextTemplate
        
class GenshiMarkupTemplateFactory(grok.components.GlobalUtility):

    zope.interface.implements(grok.interfaces.ITemplateFileFactory)
    grok.name('g')
    
    def __call__(self, filename, _prefix=None):
        return GenshiMarkupTemplate(filename=filename, _prefix=_prefix)

class GenshiTextTemplateFactory(grok.components.GlobalUtility):

    zope.interface.implements(grok.interfaces.ITemplateFileFactory)
    grok.name('gt')

    def __call__(self, filename, _prefix=None):
        return GenshiTextTemplate(filename=filename, _prefix=_prefix)
