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
$Id: _duplicate.py,v 1.5 2003/06/07 06:54:24 stevea Exp $
"""
from zope.exceptions import ZopeError, IZopeError
from zope.interface import implements

class IDuplicationError(IZopeError):
    pass

class DuplicationError(ZopeError):
    """A duplicate registration was attempted"""
    implements(IDuplicationError)
