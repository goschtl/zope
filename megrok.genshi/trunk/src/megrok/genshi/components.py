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

    def __call__(self, namespace):
        stream = self._template.generate(**namespace)
        return stream.render(self.result_type)

    def _factory_init(self, factory):
        pass
    
    def getDefaultVariables(self):
        return {}
    
    def render_template(self, view):
        namespace = view.getDefaultVariables()
        namespace.update(view.getTemplateVariables())
        return self(namespace)


class GenshiMarkupTemplate(GenshiTemplateBase):
    
    result_type = 'xhtml'
    
    def __init__(self, html):
        self._template = genshi.template.MarkupTemplate(html)
        self.__grok_module__ = martian.util.caller_module()

        
class GenshiMarkupTemplateFile(GenshiTemplateBase):

    zope.interface.implements(grok.interfaces.ITemplateFile)
    zope.interface.classProvides(grok.interfaces.ITemplateFactory)

    result_type = 'xhtml'

    def __init__(self, filename, _prefix=None):
        loader = genshi.template.TemplateLoader(_prefix)
        self._template = loader.load(filename)

grok.global_utility(GenshiMarkupTemplateFile, name='gmt', direct=True)

class GenshiTextTemplateFile(GenshiTemplateBase):

    result_type = 'xhtml'
    
    zope.interface.implements(grok.interfaces.ITemplateFile)
    zope.interface.classProvides(grok.interfaces.ITemplateFactory)
    
    def __init__(self, filename, _prefix=None):
        loader = genshi.template.TemplateLoader(_prefix)
        self._template = loader.load(filename, cls=genshi.template.TextTemplate)

grok.global_utility(GenshiTextTemplateFile, name='gtt', direct=True)