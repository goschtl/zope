##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
""" ITypeableFile implementation

$Id$
"""
from cStringIO import StringIO
from zope import interface, component
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent

from z3c.filetype import api, interfaces


class TypeableFile(object):
    interface.implements(interfaces.ITypeableFile)

    def __init__(self, data=''):
        self.data = data
        if data:
            api.applyInterfaces(self)


class TypeableFileData(object):
    interface.implements(interfaces.IFileData)
    component.adapts(interfaces.ITypeableFile)

    def __init__(self, context):
        self.context = context

    def open(self, mode=''):
        return StringIO(self.context.data)


@component.adapter(interfaces.ITypeableFile, IObjectCreatedEvent)
def handleCreated(typeableFile, event):
    """handles modification of data"""
    api.applyInterfaces(typeableFile)


@component.adapter(interfaces.ITypeableFile, IObjectModifiedEvent)
def handleModified(typeableFile, event):
    """handles modification of data"""
    if interfaces.IFileTypeModifiedEvent.providedBy(event):
        return
    api.applyInterfaces(typeableFile)
