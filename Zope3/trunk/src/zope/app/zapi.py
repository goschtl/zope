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

$Id: zapi.py,v 1.6 2003/06/13 17:41:10 stevea Exp $
"""

from zope.app.interfaces.zapi import IZAPI
from zope.interface import moduleProvides
from zope.context import getWrapperData

moduleProvides(IZAPI)
__all__ = tuple(IZAPI)

from zope.component import *
from zope.context import *
from zope.app.context import *
from zope.app.traversing import *

name = getName
