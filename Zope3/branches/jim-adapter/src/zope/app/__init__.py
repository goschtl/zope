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
"""Zope application package.

$Id$
"""
##############################################################################
# BBB 2006/04/03 -- to be removed after 12 months

import sys
from zope.deprecation import deprecated

import zope.decorator
import zope.datetime
import zope.datetime.timezones
import zope.size
import zope.size.interfaces

sys.modules['zope.app.decorator'] = deprecated(
    zope.decorator, "zope.app.decorator has been renamed to zope.decorator. "
    "This alias will be removed in Zope 3.5.")

sys.modules['zope.app.datetimeutils'] = deprecated(
    zope.datetime, "zope.app.datetimeutils has been renamed to zope.datetime. "
    "This alias will be removed in Zope 3.5.")

sys.modules['zope.app.timezones'] = deprecated(
    zope.datetime.timezones, "zope.app.timezones has been renamed to "
    "zope.datetime.timezones.  This alias will be removed in Zope 3.5.")

sys.modules['zope.app.size'] = deprecated(
    zope.size, "zope.app.size has been renamed to zope.size. This alias will "
    "be removed in Zope 3.5.")

sys.modules['zope.app.size.interfaces'] = deprecated(
    zope.size, "zope.app.size has been renamed to zope.size. This alias will "
    "be removed in Zope 3.5.")

##############################################################################
