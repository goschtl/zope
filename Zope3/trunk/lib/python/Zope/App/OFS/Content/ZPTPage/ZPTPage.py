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
$Id: ZPTPage.py,v 1.18 2002/12/20 09:25:41 srichter Exp $
"""

import re

from Interface import Interface
from Interface.Attribute import Attribute
import Zope.Schema
from Persistence import Persistent

from Zope.ContextWrapper import ContextMethod
from Zope.Proxy.ContextWrapper import getWrapperContainer
from Zope.Security.Proxy import ProxyFactory

from Zope.PageTemplate.PageTemplate import PageTemplate
from Zope.App.PageTemplate.Engine import AppPT

class IZPTPage(Interface):
    """ZPT Pages are a persistent implementation of Page Templates.

       Note: I introduced some new methods whose functionality is
             actually already covered by some other methods but I
             want to start inforcing a common coding standard.
    """

    def setSource(text, content_type='text/html'):
        """Save the source of the page template.

        'text' must be Unicode.
        """

    def getSource():
        """Get the source of the page template."""

    source = Zope.Schema.Text(
        title=u"Source",
        description=u"""The source of the page template.""",
        required=True)


class IRenderZPTPage(Interface):

    content_type = Attribute('Content type of generated output')

    def render(request, *args, **kw):
        """Render the page template.

        The first argument is bound to the top-level 'request'
        variable. The positional arguments are bound to the 'args'
        variable and the keyword arguments are bound to the 'options'
        variable.
        """


class ZPTPage(AppPT, PageTemplate, Persistent):

    __implements__ = IZPTPage, IRenderZPTPage

    def getSource(self):
        '''See interface Zope.App.OFS.ZPTPage.ZPTPage.IZPTPage'''
        return self.read()

    def setSource(self, text, content_type='text/html'):
        '''See interface Zope.App.OFS.ZPTPage.ZPTPage.IZPTPage'''
        if not isinstance(text, unicode):
            raise TypeError("source text must be Unicode")

        self.pt_edit(text.encode('utf-8'), content_type)

    def pt_getContext(self, instance, request, **_kw):
        # instance is a View component
        namespace = super(ZPTPage, self).pt_getContext(**_kw)
        namespace['request'] = request
        namespace['context'] = instance
        return namespace

    def render(self, request, *args, **keywords):
        instance = getWrapperContainer(self)

        request = ProxyFactory(request)
        instance = ProxyFactory(instance)
        if args: args = ProxyFactory(args)
        kw = ProxyFactory(keywords)

        namespace = self.pt_getContext(instance, request,
                                       args=args, options=kw)

        return self.pt_render(namespace)

    render = ContextMethod(render)

    source = property(getSource, setSource, None,
                      """Source of the Page Template.""")


# Adapter for ISearchableText
from Zope.App.index.text.interfaces import ISearchableText

class SearchableText:

    __used_for__ = IZPTPage
    __implements__ = ISearchableText

    def __init__(self, page):
        self.page = page

    def getSearchableText(self):
        text = self.page.getSource()
        if isinstance(text, str):
            text = unicode(self.page.source, 'utf-8')
        # else:
        #   text was already Unicode, which happens, but unclear how it
        #   gets converted to Unicode since the ZPTPage stores UTF-8 as
        #   an 8-bit string.
        
        
        if self.page.content_type.startswith('text/html'):
            tag = re.compile(r"<[^>]+>")
            text = tag.sub('', text)
        
           
        return [text]
