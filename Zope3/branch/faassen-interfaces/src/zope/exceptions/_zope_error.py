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
"""Base class for Zope application errors.

$Id: _zope_error.py,v 1.6 2003/06/07 06:54:24 stevea Exp $
"""
from zope.interface.common.interfaces import IException
from zope.interface import implements

class IZopeError(IException):
    pass

class ZopeError(Exception):
    """Generic base class for Zope errors."""
    implements(IZopeError)
