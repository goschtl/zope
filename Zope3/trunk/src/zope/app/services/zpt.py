##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
$Id: zpt.py,v 1.5 2003/02/07 15:52:21 jim Exp $
"""

import re

from zope.interface import Interface, Attribute
import zope.schema
from persistence import Persistent

from zope.proxy.context import ContextMethod
from zope.proxy.context import getWrapperContainer
from zope.security.proxy import ProxyFactory

from zope.app.interfaces.content.file import IFileContent
from zope.pagetemplate.pagetemplate import PageTemplate
from zope.app.pagetemplate.engine import AppPT
from zope.app.interfaces.services.interfaces import IZPTTemplate
from zope.app.interfaces.index.text import ISearchableText
from zope.app.interfaces.file import IReadFile, IWriteFile, IFileFactory

class ZPTTemplate(AppPT, PageTemplate, Persistent):

    __implements__ = IZPTTemplate

    contentType = 'text/html'
    expand = False

    source = property(
        # get
        lambda self: self.read(),
        # set
        lambda self, text: self.pt_edit(text.encode('utf-8'), self.contentType)
        )

    def pt_getContext(self, view, **_kw):
        # instance is a View component
        namespace = super(ZPTTemplate, self).pt_getContext(**_kw)
        namespace['view'] = view
        namespace['request'] = view.request
        namespace['context'] = view.context
        return namespace

    def render(self, view, *args, **keywords):

        if args:
            args = ProxyFactory(args)
        kw = ProxyFactory(keywords)

        namespace = self.pt_getContext(view, args=args, options=kw)

        return self.pt_render(namespace)

# Adapter for ISearchableText

tag = re.compile(r"<[^>]+>")
class SearchableText:

    __implements__ = ISearchableText
    __used_for__ = IZPTTemplate

    def __init__(self, page):
        self.page = page

    def getSearchableText(self):
        text = self.page.source
        if isinstance(text, str):
            text = unicode(self.page.source, 'utf-8')
        # else:
        #   text was already Unicode, which happens, but unclear how it
        #   gets converted to Unicode since the ZPTPage stores UTF-8 as
        #   an 8-bit string.

        if self.page.contentType.startswith('text/html'):
            text = tag.sub('', text)

        return [text]

# Adapters for file-system emulation

class ReadFile:

    __implements__ = IReadFile

    def __init__(self, context):
        self.context = context

    def read(self):
        return self.context.source

    def size(self):
        return len(self.context.source)
        

class WriteFile:

    __implements__ = IWriteFile

    def __init__(self, context):
        self.context = context

    def write(self, data):
        self.context.source = data


class ZPTFactory:

    __implements__ = IFileFactory

    def __init__(self, context):
        self.context = context

    def __call__(self, name, content_type, data):
        r = ZPTTemplate()
        r.source = data
        return r
