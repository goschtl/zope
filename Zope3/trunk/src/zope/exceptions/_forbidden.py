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
$Id: _forbidden.py,v 1.2 2002/12/25 14:13:38 jim Exp $
"""
from zope.exceptions import ZopeError

class Forbidden(ZopeError):
    """A resource cannot be accessed under any circumstances
    """

class ForbiddenAttribute(Forbidden, AttributeError):
    """An attribute is unavailable because it is forbidden (private)
    """
