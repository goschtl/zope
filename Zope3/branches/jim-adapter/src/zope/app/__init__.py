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
import sys
from zope.deprecation import deprecated

import zope.decorator
import zope.datetime
import zope.datetime.timezones

sys.modules['zope.app.decorator'] = deprecated(
    zope.decorator, "zope.app.decorator has been renamed to zope.decorator.")

sys.modules['zope.app.datetimeutils'] = deprecated(
    zope.datetime, "zope.app.datetimeutils has been renamed to zope.datetime.")

sys.modules['zope.app.timezones'] = deprecated(
    zope.datetime.timezones, "zope.app.timezones has been renamed to "
    "zope.datetime.timezones.")
