##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
# 
##############################################################################
"""
$Id: DTMLPage.py,v 1.2 2002/07/19 13:12:31 srichter Exp $
"""
from Interface import Interface
from Interface.Attribute import Attribute
import Schema
from Persistence import Persistent

from Zope.ContextWrapper import ContextMethod
from Zope.Proxy.ContextWrapper import getWrapperContainer
from Zope.Security.Proxy import ProxyFactory

from Zope.DocumentTemplate.pDocumentTemplate import MultiMapping
from Zope.DocumentTemplate.DT_HTML import HTML
from Zope.App.OFS.Annotation.IAnnotatable import IAnnotatable
from Zope.App.OFS.Content.IFileContent import IFileContent


class IDTMLPage(Interface):
    """DTML Pages are a persistent implementation of DTML."""
    
    def setSource(text, content_type='text/html'):
        """Save the source of the page template."""

    def getSource():
        """Get the source of the page template."""


class SDTMLPage(Schema.Schema):
    source = Schema.Str(
        id="source",
        title="Source",
        description="""The source od the page template.""",
        required=1)


class IRenderDTMLPage(Interface):

    content_type = Attribute('Content type of generated output')

    def render(request, *args, **kw):
        """Render the page template.

        The first argument is bound to the top-level 'request'
        variable. The positional arguments are bound to the 'args'
        variable and the keyword arguments are bound to the 'options'
        variable.
        """


class DTMLPage(Persistent):

    # XXX Putting IFileContent at the end gives an error!
    __implements__ = IFileContent, IDTMLPage, SDTMLPage, IRenderDTMLPage, \
                     IAnnotatable


    def __init__(self, source=''):
        self.setSource(source)

    def getSource(self):
        '''See interface IDTMLPage'''
        return self.template.read()

    def setSource(self, text, content_type='text/html'):
        '''See interface IDTMLPage'''
        self.template = HTML(text.encode('utf-8'))
        self.content_type = content_type

    def render(self, request, *args, **kw):
        """See interface IDTMLRenderPage"""

        instance = ProxyFactory(getWrapperContainer(self))
        request = ProxyFactory(request)
        
        for k in kw:
            kw[k] = ProxyFactory(kw[k])
        kw['REQUEST'] = request

        return self.template(instance, request, **kw)


    render = ContextMethod(render)

    __call__ = render

    source = property(getSource, setSource, None,
                      """Source of the DTML Page.""")
