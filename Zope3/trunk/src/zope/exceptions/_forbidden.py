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

$Id: _forbidden.py,v 1.4 2003/02/11 16:00:06 sidnei Exp $
"""
from zope.exceptions import ZopeError, IZopeError
from zope.interface.implements import implements
from zope.interface.common.interfaces import IAttributeError

class Forbidden(ZopeError):
    """A resource cannot be accessed under any circumstances
    """

class IForbidden(IZopeError):
    pass

class ForbiddenAttribute(Forbidden, AttributeError):
    """An attribute is unavailable because it is forbidden (private)
    """
class IForbiddenAttribute(IForbidden, IAttributeError):
    pass

implements(Forbidden, IForbidden)
implements(ForbiddenAttribute, IForbiddenAttribute)
