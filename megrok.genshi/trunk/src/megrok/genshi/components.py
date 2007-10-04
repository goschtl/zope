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

class GenshiMarkupTemplate(grok.components.GrokPageTemplate):

    zope.interface.implements(grok.interfaces.ITemplateFile)
    
    def __init__(self, filename=None, _prefix=None, html=None):
        if ((html is not None and filename is not None) or
            (html is None and filename is None)):
            raise AssertionError("You must pass either html or filename but not both.")
        
        if html is not None:
            self._template = genshi.template.MarkupTemplate(html)
        else:
            loader = genshi.template.TemplateLoader(_prefix)
            self._template = loader.load(filename)
            
    
    def __call__(self, namespace):
        stream = self._template.generate(**namespace)
        return stream.render('xhtml')
    
    def _factory_init(self, factory):
        pass
    
    def render_template(self, view):
        namespace = view.getDefaultVariables()
        namespace.update(view.getTemplateVariables())
        return self(namespace)
