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
$Id: dtmlpage.py,v 1.3 2003/01/06 15:46:26 srichter Exp $
"""
from persistence import Persistent

from zope.app.interfaces.annotation import IAnnotatable
from zope.app.interfaces.content.file import IFileContent
from zope.app.interfaces.content.dtmlpage import IDTMLPage, IRenderDTMLPage

from zope.proxy.context import ContextMethod
from zope.proxy.context import getWrapperContainer
from zope.security.proxy import ProxyFactory

from zope.documenttemplate.dt_html import HTML

class DTMLPage(Persistent):

    # XXX Putting IFileContent at the end gives an error!
    __implements__ = IFileContent, IDTMLPage, IRenderDTMLPage, IAnnotatable

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
