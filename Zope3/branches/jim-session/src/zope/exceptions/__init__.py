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
"""General exceptions that wish they were standard exceptions

These exceptions are so general purpose that they don't belong in Zope
application-specific packages.

$Id$
"""
# This module should be independent of I18n, so let's not require it.
try:
    from zope.i18n import MessageIDFactory
except ImportError:
    ZopeMessageIDFactory = unicode
else:
    # Import _ to use to create message ids in the zope domain
    ZopeMessageIDFactory = MessageIDFactory('zope')

from zope.exceptions._zope_error import ZopeError, IZopeError
from zope.exceptions.unauthorized import Unauthorized, IUnauthorized
from zope.exceptions._notfounderror import NotFoundError, INotFoundError
from zope.exceptions._forbidden import Forbidden, ForbiddenAttribute
from zope.exceptions._forbidden import IForbidden, IForbiddenAttribute
from zope.exceptions._duplicate import DuplicationError, IDuplicationError
