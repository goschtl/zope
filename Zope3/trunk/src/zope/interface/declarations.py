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
"""Interfaces declarations, forward comptability versions

$Id: declarations.py,v 1.2 2003/04/30 20:13:23 jim Exp $
"""

import sys
from types import ClassType
_ClassTypes = ClassType, type
del ClassType

def directlyProvides(ob, *interfaces):
    
    if isinstance(ob, _ClassTypes):
        ob.__class_implements__ = interfaces
        return


    #XXX this is really a hack. interfacegeddon will hopefully provide a better
    # way to do this
    
    # if there are no interfaces, then we go back to whatever the class
    # implements
    if not interfaces:
        try:
            del ob.__implements__
        except AttributeError:
            pass
        return

    cls = ob.__class__
    implements = getattr(cls, '__implements__', ())
    if isinstance(implements, tuple):
        implements = list(implements)
    else:
        implements = [implements]

    orig_implements = implements[:]
        
    for interface in interfaces:
        if interface not in implements:
            implements.append(interface)

    # if there are no changes in the interfaces, go back to whatever
    # the class implements
    if implements == orig_implements:
        try:
            del ob.__implements__
        except AttributeError:
            pass
        return

    ob.__implements__ = tuple(implements)


def classProvides(*interfaces):
    f = sys._getframe(1)
    locals = f.f_locals
    if f.f_globals is locals or "__module__" not in locals:
        raise TypeError("classProvides can only be used in a class definition")
    if "__class_implements__" in locals:
        raise TypeError("classProvides can only be used once "
                        "in a class definition")
    locals["__class_implements__"] = interfaces

def moduleProvides(*interfaces):
    f = sys._getframe(1)
    locals = f.f_locals
    if f.f_globals is not locals or "__name__" not in locals:
        raise TypeError(
            "classProvides can only be used in a module definition")
    if "__implements__" in locals:
        raise TypeError("moduleProvides can only be used once "
                        "in a module definition")
    locals["__implements__"] = interfaces
