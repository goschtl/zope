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
$Id: _duplicate.py,v 1.3 2003/02/04 20:21:59 stevea Exp $
"""
from zope.exceptions import ZopeError, IZopeError
from zope.interface.implements import implements

class DuplicationError(ZopeError):
    """A duplicate registration was attempted"""

class IDuplicationError(IZopeError):
    pass

implements(DuplicationError, IDuplicationError)
