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
"""Factory object

$Id$
"""
from zope.interface import implements, implementedBy
from zope.component.interfaces import IFactory

class Factory(object):
    """Generic factory implementation.

    The purpose of this implementation is to provide a quick way of creating
    factories for classes, functions and other objects.
    """
    implements(IFactory)

    def __init__(self, callable, title='', description=''):
        self._callable = callable
        self.title = title
        self.description = description

    def __call__(self, *args, **kw):
        return self._callable(*args, **kw)

    def getInterfaces(self):
        try:
            return implementedBy(self._callable)
        except TypeError:
            # XXX This is a hack
            # We really only support classes
            return implementedBy(object())
