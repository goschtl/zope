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
"""Persistent PageTemplate-based View

$Id$
"""
import re

from zope.security.proxy import ProxyFactory
from persistent import Persistent
from zope.interface import Interface, implements
from zope.schema import Text, BytesLine, Bool

from zope.app.container.contained import Contained
from zope.app.registration.interfaces import IRegisterable
from zope.fssync.server.entryadapter import ObjectEntryAdapter, AttrMapping
from zope.fssync.server.interfaces import IObjectFile
from zope.app.filerepresentation.interfaces import IReadFile, IWriteFile
from zope.app.filerepresentation.interfaces import IFileFactory
from zope.app.pagetemplate.engine import AppPT
from zope.pagetemplate.pagetemplate import PageTemplate

class IZPTInfo(Interface):
    """ZPT Template configuration information
    """

    contentType = BytesLine(
        title=u'Content type of generated output',
        required=True,
        default='text/html'
        )

    source = Text(
        title=u"Source",
        description=u"""The source of the page template.""",
        required=True)

    expand = Bool(
        title=u"Expand macros",
        )

class IZPTTemplate(IZPTInfo, IRegisterable):
    """ZPT Templates for use in views"""

    def render(context, request, *args, **kw):
        """Render the page template.

        The context argument is bound to the top-level 'context'
        variable.  The request argument is bound to the top-level
        'request' variable. The positional arguments are bound to the
        'args' variable and the keyword arguments are bound to the
        'options' variable.

        """

class ZPTTemplate(AppPT, PageTemplate, Persistent, Contained):

    implements(IZPTTemplate)

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

# Adapters for file-system emulation

class ReadFile:

    implements(IReadFile)

    def __init__(self, context):
        self.context = context

    def read(self):
        return self.context.source

    def size(self):
        return len(self.context.source)


class WriteFile:

    implements(IWriteFile)

    def __init__(self, context):
        self.context = context

    def write(self, data):
        self.context.source = data


class ZPTFactory:

    implements(IFileFactory)

    def __init__(self, context):
        self.context = context

    def __call__(self, name, content_type, data):
        r = ZPTTemplate()
        r.source = data
        return r


class ZPTPageAdapter(ObjectEntryAdapter):
    """ObjectFile adapter for ZPTTemplate objects."""

    implements(IObjectFile)

    def getBody(self):
        return self.context.source

    def setBody(self, data):
        # Convert the data to Unicode, since that's what ZPTTemplate
        # wants; it's normally read from a file so it'll be bytes.
        # XXX This will die if it's not ASCII.  Guess encoding???
        self.context.source = unicode(data)

    def extra(self):
        return AttrMapping(self.context, ('contentType', 'expand'))
