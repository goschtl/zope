##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Collection of many common api functions

Makes imports easier

$Id: __init__.py,v 1.1 2004/03/15 12:03:45 srichter Exp $
"""

from interfaces import IZAPI
from zope.interface import moduleProvides
from zope.app import servicenames

moduleProvides(IZAPI)
__all__ = tuple(IZAPI)

from zope.component import *

from zope.app.traversing import *
from zope.app.exception.interfaces import UserError

name = getName
