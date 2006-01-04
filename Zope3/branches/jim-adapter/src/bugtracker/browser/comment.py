##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Structured Text Renderer Classes

$Id: comment.py,v 1.2 2003/08/12 22:50:57 srichter Exp $
"""
import re

from zope.proxy import removeAllProxies
from zope.schema.vocabulary import getVocabularyRegistry
from zope.structuredtext.document import Document
from zope.structuredtext.html import HTML

from zope.app import zapi
from zope.app.dublincore.interfaces import IZopeDublinCore


class CommentViewBase(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def creator(self):
        dc = IZopeDublinCore(self.context)
        registry = getVocabularyRegistry()
        users = registry.get(self.context, 'Users')
        id = dc.creators[0]
        try:
            return users.getTerm(id).principal
        except LookupError:
            # There is no principal for this id, so let's just fake one.
            return {'id': id, 'login': id, 'title': id, 'description': id}

    def modified(self):
        dc = IZopeDublinCore(self.context)
        formatter = self.request.locale.dates.getFormatter('dateTime', 'short')
        if dc.modified is None:
            return formatter.format(dc.created)
        return formatter.format(dc.modified)

    def body(self):
        ttype = getattr(self.context.body, 'ttype', None)
        if ttype is not None:
            source = zapi.createObject(self.context.body.ttype,
                                       self.context.body)
            view = zapi.getMultiAdapter(
                (removeAllProxies(source), self.request))
            html = view.render()
        else:
            html = self.context.body
        return html
