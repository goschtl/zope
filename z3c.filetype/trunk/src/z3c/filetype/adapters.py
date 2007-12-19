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
"""

$Id$
"""
from zope import interface, component

import interfaces
from interfaces import filetypes


class TypedFileType(object):
    component.adapts(filetypes.ITypedFile)
    interface.implements(interfaces.IFileType)

    def __init__(self, context):
        self.context = context

    @property
    def contentType(self):
        decl = interface.Declaration(
            *interface.directlyProvidedBy(self.context))
        for iface in decl.flattened():
            if not issubclass(iface, filetypes.ITypedFile):
                continue
            mt = iface.queryTaggedValue(filetypes.MT)
            if mt is not None:
                return mt
