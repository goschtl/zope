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
$Id: zpt.py,v 1.4 2003/02/03 20:57:47 jim Exp $
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
