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
"""Support for interface declarations on decorators

>>> from zope.context import Wrapper
>>> from zope.interface import *
>>> class I1(Interface):
...     pass
>>> class I2(Interface):
...     pass
>>> class I3(Interface):
...     pass
>>> class I4(Interface):
...     pass

>>> class D1(Wrapper):
...   implements(I1)


>>> class D2(Wrapper):
...   implements(I2)

>>> class X:
...   implements(I3)

>>> x = X()
>>> directlyProvides(x, I4)

Interfaces of X are ordered with the directly-provided interfaces first

>>> [interface.__name__ for interface in list(providedBy(x))]
['I4', 'I3']

When we decorate objects, what order should the interfaces come in?
One could argue that decorators are less specific, so they should come last.

>>> [interface.__name__ for interface in list(providedBy(D1(x)))]
['I4', 'I3', 'I1']

>>> [interface.__name__ for interface in list(providedBy(D2(D1(x))))]
['I4', 'I3', 'I1', 'I2']

$Id: declarations.py,v 1.1 2003/05/31 22:12:38 jim Exp $
"""

from zope.proxy import getProxiedObject
from zope.interface import providedBy
from zope.interface.declarations import getObjectSpecification
from zope.interface.declarations import ObjectSpecification
from zope.interface.declarations import ObjectSpecificationDescriptor

class DecoratorSpecificationDescriptor(ObjectSpecificationDescriptor):

    def __get__(self, inst, cls):
        if inst is None:
            return getObjectSpecification(cls)
        else:
            provided = providedBy(getProxiedObject(inst))

            # Use type rather than __class__ because inst is a proxy and
            # will return the proxied object's class.
            cls = type(inst) 
            return ObjectSpecification(provided, cls)

decoratorSpecificationDescriptor = DecoratorSpecificationDescriptor()
