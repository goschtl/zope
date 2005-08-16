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

$Id: _forbidden.py,v 1.5 2003/06/07 06:54:24 stevea Exp $
"""
from zope.exceptions import ZopeError, IZopeError
from zope.interface import implements
from zope.interface.common.interfaces import IAttributeError

class IForbidden(IZopeError):
    pass

class Forbidden(ZopeError):
    """A resource cannot be accessed under any circumstances
    """
    implements(IForbidden)

class IForbiddenAttribute(IForbidden, IAttributeError):
    pass

class ForbiddenAttribute(Forbidden, AttributeError):
    """An attribute is unavailable because it is forbidden (private)
    """
    implements(IForbiddenAttribute)

