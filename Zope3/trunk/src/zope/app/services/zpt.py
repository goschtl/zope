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
$Id: zpt.py,v 1.17 2004/01/13 19:32:23 fdrake Exp $
"""

from zope.security.proxy import ProxyFactory
import persistence
import re
import zope.app.container.contained
import zope.fssync.server.entryadapter
import zope.fssync.server.interfaces
import zope.app.interfaces.file
import zope.app.interfaces.index.text
import zope.app.interfaces.services.registration
import zope.app.pagetemplate.engine
import zope.interface
import zope.pagetemplate.pagetemplate
import zope.schema

class IZPTTemplate(zope.app.interfaces.services.registration.IRegisterable):
    """ZPT Templates for use in views
    """

    contentType = zope.schema.BytesLine(
        title=u'Content type of generated output',
        required=True,
        default='text/html'
        )

    source = zope.schema.Text(
        title=u"Source",
        description=u"""The source of the page template.""",
        required=True)

    expand = zope.schema.Bool(
        title=u"Expand macros",
        )

    def render(context, request, *args, **kw):
        """Render the page template.

        The context argument is bound to the top-level 'context'
        variable.  The request argument is bound to the top-level
        'request' variable. The positional arguments are bound to the
        'args' variable and the keyword arguments are bound to the
        'options' variable.

        """

class ZPTTemplate(
    zope.app.pagetemplate.engine.AppPT,
    zope.pagetemplate.pagetemplate.PageTemplate,
    persistence.Persistent,
    zope.app.container.contained.Contained,
    ):

    zope.interface.implements(IZPTTemplate)

    contentType = 'text/html'
    expand = False
    usage = u''

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

        if self.usage:
            if "template_usage" not in keywords:
                kw = {'template_usage': self.usage}
                kw.update(keywords)
                keywords = kw

        kw = ProxyFactory(keywords)

        namespace = self.pt_getContext(view, args=args, options=kw)

        return self.pt_render(namespace)

# Adapter for ISearchableText

tag = re.compile(r"<[^>]+>")
class SearchableText:

    zope.interface.implements(zope.app.interfaces.index.text.ISearchableText)
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

    zope.interface.implements(zope.app.interfaces.file.IReadFile)

    def __init__(self, context):
        self.context = context

    def read(self):
        return self.context.source

    def size(self):
        return len(self.context.source)


class WriteFile:

    zope.interface.implements(zope.app.interfaces.file.IWriteFile)

    def __init__(self, context):
        self.context = context

    def write(self, data):
        self.context.source = data


class ZPTFactory:

    zope.interface.implements(zope.app.interfaces.file.IFileFactory)

    def __init__(self, context):
        self.context = context

    def __call__(self, name, content_type, data):
        r = ZPTTemplate()
        r.source = data
        return r


class ZPTPageAdapter(zope.fssync.server.entryadapter.ObjectEntryAdapter):
    """ObjectFile adapter for ZPTTemplate objects."""

    zope.interface.implements(zope.fssync.server.entryadapter.IObjectFile)

    def getBody(self):
        return self.context.source

    def setBody(self, data):
        # Convert the data to Unicode, since that's what ZPTTemplate
        # wants; it's normally read from a file so it'll be bytes.
        # XXX This will die if it's not ASCII.  Guess encoding???
        self.context.source = unicode(data)

    def extra(self):
        return zope.fssync.server.entryadapter.AttrMapping(
            self.context, ('contentType', 'expand'))
