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

$Id: declarations.py,v 1.1 2003/04/18 22:12:32 jim Exp $
"""

import sys
from types import ClassType
_ClassTypes = ClassType, type
del ClassType

def directlyProvides(object, *interfaces):
    if isinstance(object, _ClassTypes):
        object.__class_implements__ = interfaces
    else:
        object.__implements__ = interfaces

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
