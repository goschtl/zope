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
"""Implementation of the Zope TALES API


$Id: talesapi.py,v 1.7 2003/09/16 22:11:26 srichter Exp $
"""
from zope.app.interfaces.talesapi import IZopeTalesAPI
from zope.app.interfaces.dublincore import IZopeDublinCore
from zope.app.interfaces.size import ISized
from zope.app import zapi
from zope.interface import implements
from zope.tales.interfaces import ITALESFunctionNamespace

class ZopeTalesAPI(object):

    implements(IZopeTalesAPI, ITALESFunctionNamespace)

    def __init__(self, context):
        self.context = context

    def setEngine(self, engine):
        self._engine = engine

    def title(self):
        a = zapi.queryAdapter(self.context, IZopeDublinCore)
        if a is None:
            raise AttributeError, 'title'
        return a.title
    title = property(title)

    def description(self):
        a = zapi.queryAdapter(self.context, IZopeDublinCore)
        if a is None:
            raise AttributeError, 'description'
        return a.description
    description = property(description)

    def created(self):
        a = zapi.queryAdapter(self.context, IZopeDublinCore)
        if a is None:
            raise AttributeError, 'created'
        return a.created
    created = property(created)

    def modified(self):
        a = zapi.queryAdapter(self.context, IZopeDublinCore)
        if a is None:
            raise AttributeError, 'modified'
        return a.modified
    modified = property(modified)

    def name(self):
        return zapi.name(self.context)

    def title_or_name(self):
        return getattr(self, 'title', '') or zapi.name(self.context)

    def size(self):
        a = zapi.queryAdapter(self.context, ISized)
        if a is None:
            raise AttributeError, 'created'
        return a.sizeForDisplay()

