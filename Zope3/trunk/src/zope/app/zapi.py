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

$Id: zapi.py,v 1.12 2003/11/21 17:10:48 jim Exp $
"""

from zope.app.interfaces.zapi import IZAPI
from zope.interface import moduleProvides
from zope.app.services import servicenames

moduleProvides(IZAPI)
__all__ = tuple(IZAPI)

from zope.component import *

# XXX: 'queryService' is not part of IComponentArchitecture;
# XXX: Jim says you shouldn't need it anyway.
# YYY: So why is it here?

from zope.component import queryService

from zope.app.traversing import *
from zope.app.interfaces.exceptions import UserError

name = getName
