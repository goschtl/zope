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
"""

$Id: factory.py,v 1.3 2003/06/06 19:29:08 stevea Exp $
"""
from zope.component.interfaces import IFactory
from zope.interface import Interface, implements, implementedBy

class IX(Interface):
    """the dummy interface which class X supposedly implements,
    according to the factory"""

class X:
    implements(IX)
    def __init__(self, *args, **kwargs):
        self.args=args
        self.kwargs=kwargs


class ClassFactoryWrapper:
    implements(IFactory)
    def __init__(self, klass):
        self.__klass=klass
    def __call__(self, *args, **kwargs):
        return self.__klass(*args, **kwargs)
    def getInterfaces(self):
        return implementedBy(self.__klass)

f=ClassFactoryWrapper(X)
