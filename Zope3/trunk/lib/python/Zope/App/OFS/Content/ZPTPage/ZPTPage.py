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
$Id: ZPTPage.py,v 1.15 2002/12/05 15:52:44 fdrake Exp $
"""
from Interface import Interface
from Interface.Attribute import Attribute
import Zope.Schema
from Persistence import Persistent

from Zope.ContextWrapper import ContextMethod
from Zope.Proxy.ContextWrapper import getWrapperContainer
from Zope.Security.Proxy import ProxyFactory

from Zope.App.OFS.Content.IFileContent import IFileContent
from Zope.PageTemplate.PageTemplate import PageTemplate
from Zope.App.PageTemplate.Engine import AppPT

class IZPTPage(Interface):
    """ZPT Pages are a persistent implementation of Page Templates.

       Note: I introduced some new methods whose functionality is
             actually already covered by some other methods but I
             want to start inforcing a common coding standard.
    """

    def setSource(text, content_type='text/html'):
        """Save the source of the page template."""

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

    # XXX Putting IFileContent at the end gives an error!
    __implements__ = IFileContent, IZPTPage, IRenderZPTPage

    def getSource(self):
        '''See interface Zope.App.OFS.ZPTPage.ZPTPage.IZPTPage'''
        return self.read()

    def setSource(self, text, content_type='text/html'):
        '''See interface Zope.App.OFS.ZPTPage.ZPTPage.IZPTPage'''
        if isinstance(text, unicode):
            text = text.encode('utf-8')

        self.pt_edit(text, content_type)

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

    __implements__ = ISearchableText
    __used_for__ = IZPTPage

    def __init__(self, page):
        self.page = page

    def getSearchableText(self):
        try:
            # XXX check about encoding here and in the ZPTPage.read
            #     the exception should go away when we know how this
            #     works in terms of conversion, for now on problems
            #     don't index the object
            return [unicode(self.page.source)]
        except:
            return None
