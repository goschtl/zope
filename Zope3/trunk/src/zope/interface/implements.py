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
"""Implemantation assertion facilities.

Revision information:
$Id: implements.py,v 1.5 2003/05/03 16:36:05 jim Exp $
"""

from zope.interface.declarations import providedBy, implementedBy
from zope.interface.declarations import classImplements
from zope.interface.declarations import InterfaceSpecification


from zope.interface import exceptions
from zope.interface.verify import verifyClass
from zope.interface.interface import InterfaceClass
from types import TupleType, ClassType, StringType

getImplements = providedBy
getImplementsOfInstances = implementedBy

def visitImplements(implements, object, visitor):
    """Call visitor for each interace.

    Visits the interfaces described by an __implements__ attribute,
    invoking the visitor for each interface object.
    If the visitor returns anything true, the loop stops.
    This does not, and should not, visit superinterfaces.
    """

    for interface in InterfaceSpecification(implements):
        if visitor(interface):
            break


assertTypeImplements = classImplements

objectImplements = providedBy
instancesOfObjectImplements = implementedBy

def _flatten(i, append):
    if InterfaceClass in i.__class__.__mro__:
        append(i)
        bases = i.getBases()
        if bases:
            for b in bases:
                _flatten(b, append)
    else:
        for iface in i:
            _flatten(iface, append)

def flattenInterfaces(interfaces, remove_duplicates=1):
    res = []
    _flatten(interfaces, res.append)
    if remove_duplicates:
        # Remove duplicates in reverse.
        # Similar to Python 2.2's method resolution order.
        seen = {}
        index = len(res) - 1
        while index >= 0:
            i = res[index]
            if i in seen:
                del res[index]
            else:
                seen[i] = 1
            index = index - 1
    return res

def implements(klass, interface, check=1):
    if check:
        verifyClass(interface, klass, tentative=1)

    old = getattr(klass, '__implements__', None)
    if old is None:
        klass.__implements__ = interface
    else:
        klass.__implements__ = old, interface
