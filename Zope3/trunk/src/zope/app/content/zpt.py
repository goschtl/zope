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
$Id: zpt.py,v 1.6 2003/02/03 15:08:32 jim Exp $
"""

import re

from persistence import Persistent

from zope.proxy.context import ContextMethod
from zope.proxy.context import getWrapperContainer
from zope.security.proxy import ProxyFactory

from zope.pagetemplate.pagetemplate import PageTemplate
from zope.app.pagetemplate.engine import AppPT
from zope.app.interfaces.index.text import ISearchableText
from zope.app.interfaces.size import ISized
from zope.app.interfaces.content.zpt import IZPTPage, IRenderZPTPage

from zope.app.interfaces.file import IReadFile, IWriteFile, IFileFactory

__metaclass__ = type

class ZPTPage(AppPT, PageTemplate, Persistent):

    __implements__ = IZPTPage, IRenderZPTPage

    expand = False

    def getSource(self):
        '''See IZPTPage'''
        return self.read()

    def setSource(self, text, content_type='text/html'):
        '''See IZPTPage'''
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

class Sized:

    __implements__ = ISized

    def __init__(self, page):
        self.num_lines = len(page.getSource().splitlines())

    def sizeForSorting(self):
        'See ISized'
        return ('line', self.num_lines)

    def sizeForDisplay(self):
        'See ISized'
        if self.num_lines == 1:
            return '1 line'
        return '%s lines' % self.num_lines

# File-system access adapters

class ZPTReadFile:

    __implements__ = IReadFile

    def __init__(self, context):
        self.context = context

    def read(self):
        return self.context.getSource()

    def size(self):
        return len(self.read())

class ZPTWriteFile:

    __implements__ = IWriteFile

    def __init__(self, context):
        self.context = context

    def write(self, data):
        # XXX Hm, how does one figure out an ftp encoding. Waaa.
        self.context.setSource(unicode(data), None)

class ZPTFactory:

    __implements__ = IFileFactory


    def __init__(self, context):
        self.context = context

    def __call__(self, name, content_type, data):
        r = ZPTPage()
        # XXX Hm, how does one figure out an ftp encoding. Waaa.
        r.setSource(unicode(data), content_type or 'text/html')
        return r
