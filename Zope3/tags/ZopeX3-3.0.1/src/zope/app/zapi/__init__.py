##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Collection of many common api functions

Makes imports easier

$Id$
"""

from interfaces import IZAPI
from zope.interface import moduleProvides

from zope.security.proxy import isinstance

from zope.app import servicenames
from zope.app.interface import queryType

moduleProvides(IZAPI)
__all__ = tuple(IZAPI)

from zope.component import *

from zope.app.traversing.api import *
from zope.app.traversing.browser.absoluteurl import absoluteURL
from zope.app.exception.interfaces import UserError

name = getName
