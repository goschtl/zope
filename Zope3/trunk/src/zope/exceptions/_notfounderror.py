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
$Id: _notfounderror.py,v 1.5 2003/02/19 15:25:58 stevea Exp $
"""
from zope.exceptions import ZopeError, IZopeError
from zope.interface.common.interfaces import IKeyError

class INotFoundError(IZopeError, IKeyError):
    pass

class NotFoundError(ZopeError, KeyError):
    """A resource could not be found.
    """
    __implements__ = INotFoundError

