##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Unauthorized Exception definition

$Id$
"""
from zope.exceptions import ZopeError
from zope.exceptions import IZopeError
from zope.interface import implements

class IUnauthorized(IZopeError):
    pass

class Unauthorized(ZopeError):
    """Some user wasn't allowed to access a resource"""

    implements(IUnauthorized)
