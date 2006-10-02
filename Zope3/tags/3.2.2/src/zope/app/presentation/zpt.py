##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Persistent PageTemplate-based View

$Id$
"""
__docformat__ = 'restructuredtext'
import persistent
import re

import zope.interface
import zope.security.proxy
from zope.pagetemplate.pagetemplate import PageTemplate

import zope.app.filerepresentation.interfaces

from zope.app import zapi
from zope.app.component.interfaces.registration import IRegisterable
from zope.app.container.contained import Contained
from zope.app.pagetemplate.engine import AppPT

import interfaces

class ZPTTemplate(AppPT, PageTemplate, persistent.Persistent, Contained):

    zope.interface.implements(interfaces.IZPTTemplate)

    contentType = 'text/html'
    expand = False

    def getSource(self):
        """See `zope.app.presentation.zpt.IZPTInfo`"""
        return self.read()

    def setSource(self, text):
        """See `zope.app.presentation.zpt.IZPTInfo`"""
        if not isinstance(text, unicode):
            raise TypeError("source text must be Unicode" , text)
        self.pt_edit(text, self.contentType)

    # See zope.app.presentation.interfaces.IZPTInfo
    source = property(getSource, setSource)

    def pt_getContext(self, view, **_kw):
        # instance is a View component
        namespace = super(ZPTTemplate, self).pt_getContext(**_kw)
        namespace['view'] = view
        namespace['request'] = view.request
        namespace['context'] = view.context
        return namespace

    def pt_source_file(self):
        try:
            return zapi.getPath(self)
        except TypeError:
            return None

    def render(self, view, *args, **keywords):

        if args:
            args = zope.security.proxy.ProxyFactory(args)

        kw = zope.security.proxy.ProxyFactory(keywords)

        namespace = self.pt_getContext(view, args=args, options=kw)
        debug_flags = view.request.debug

        return self.pt_render(namespace, showtal=debug_flags.showTAL,
                              sourceAnnotations=debug_flags.sourceAnnotations)


# Adapters for file-system emulation
class ReadFile(object):

    zope.interface.implements(
        zope.app.filerepresentation.interfaces.IReadFile)

    def __init__(self, context):
        self.context = context

    def read(self):
        return self.context.source

    def size(self):
        return len(self.context.source)


class WriteFile(object):

    zope.interface.implements(
        zope.app.filerepresentation.interfaces.IWriteFile)

    def __init__(self, context):
        self.context = context

    def write(self, data):
        self.context.source = data


class ZPTFactory(object):

    zope.interface.implements(
        zope.app.filerepresentation.interfaces.IFileFactory)

    def __init__(self, context):
        self.context = context

    def __call__(self, name, content_type, data):
        template = ZPTTemplate()
        template.source = data
        return template
