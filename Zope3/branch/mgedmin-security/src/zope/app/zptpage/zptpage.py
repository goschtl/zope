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
$Id: zptpage.py,v 1.7 2004/03/19 23:35:04 srichter Exp $
"""
import re

from persistent import Persistent

from zope.proxy import removeAllProxies
from zope.security.proxy import ProxyFactory
from zope.interface import implements
from zope.pagetemplate.pagetemplate import PageTemplate

from zope.app.pagetemplate.engine import AppPT
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.index.interfaces.text import ISearchableText
from zope.app.size.interfaces import ISized
from zope.app.filerepresentation.interfaces import IReadFile, IWriteFile
from zope.app.filerepresentation.interfaces import IFileFactory
from zope.app.container.contained import Contained

from interfaces import IZPTPage, IRenderZPTPage

__metaclass__ = type

class ZPTPage(AppPT, PageTemplate, Persistent, Contained):

    implements(IZPTPage, IRenderZPTPage)

    # See zope.app.zptpage.interfaces.IZPTPage
    expand = False

    # See zope.app.zptpage.interfaces.IZPTPage
    evaluateInlineCode = False

    def getSource(self):
        """See zope.app.zptpage.interfaces.IZPTPage"""
        return self.read()

    def setSource(self, text, content_type='text/html'):
        """See zope.app.zptpage.interfaces.IZPTPage"""
        if not isinstance(text, unicode):
            raise TypeError("source text must be Unicode" , text)
        self.pt_edit(text, content_type)

    # See zope.app.zptpage.interfaces.IZPTPage
    source = property(getSource, setSource, None,
                      """Source of the Page Template.""")

    def pt_getEngineContext(self, namespace):
        context = self.pt_getEngine().getContext(namespace)
        context.evaluateInlineCode = self.evaluateInlineCode
        return context

    def pt_getContext(self, instance, request, **_kw):
        # instance is a View component
        self = removeAllProxies(self)
        namespace = super(ZPTPage, self).pt_getContext(**_kw)
        namespace['template'] = self
        namespace['request'] = request
        namespace['container'] = namespace['context'] = instance
        return namespace

    def render(self, request, *args, **keywords):
        instance = self.__parent__

        request = ProxyFactory(request)
        instance = ProxyFactory(instance)
        if args: args = ProxyFactory(args)
        kw = ProxyFactory(keywords)

        namespace = self.pt_getContext(instance, request,
                                       args=args, options=kw)

        return self.pt_render(namespace)

    source = property(getSource, setSource, None,
                      """Source of the Page Template.""")


class SearchableText:

    __used_for__ = IZPTPage
    implements(ISearchableText)

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

class Sized:

    implements(ISized)

    def __init__(self, page):
        self.num_lines = len(page.getSource().splitlines())

    def sizeForSorting(self):
        'See ISized'
        return ('line', self.num_lines)

    def sizeForDisplay(self):
        'See ISized'
        if self.num_lines == 1:
            return _('1 line')
        lines  = _('${lines} lines')
        lines.mapping = {'lines': str(self.num_lines)}
        return lines

# File-system access adapters

class ZPTReadFile:

    implements(IReadFile)

    def __init__(self, context):
        self.context = context

    def read(self):
        return self.context.getSource()

    def size(self):
        return len(self.read())

class ZPTWriteFile:

    implements(IWriteFile)

    def __init__(self, context):
        self.context = context

    def write(self, data):
        # XXX Hm, how does one figure out an ftp encoding. Waaa.
        self.context.setSource(unicode(data), None)

class ZPTFactory:

    implements(IFileFactory)


    def __init__(self, context):
        self.context = context

    def __call__(self, name, content_type, data):
        r = ZPTPage()
        # XXX Hm, how does one figure out an ftp encoding. Waaa.
        r.setSource(unicode(data), content_type or 'text/html')
        return r

class ZPTSourceView:

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __str__(self):
        return self.context.getSource()

    __call__ = __str__
