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
$Id: _notfounderror.py,v 1.6 2003/06/03 15:35:28 stevea Exp $
"""
from zope.exceptions import ZopeError, IZopeError
from zope.interface.common.interfaces import IKeyError
from zope.interface import implements

class INotFoundError(IZopeError, IKeyError):
    pass

class NotFoundError(ZopeError, KeyError):
    """A resource could not be found.
    """
    implements(INotFoundError)

