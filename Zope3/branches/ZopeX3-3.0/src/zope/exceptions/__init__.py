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

from zope.exceptions._notfounderror import NotFoundError, INotFoundError
from zope.exceptions._duplicate import DuplicationError, IDuplicationError

# Importing these interfaces from here is deprecated!

# avoid hard depency on zope.security:
try:
    from zope.security.interfaces import IUnauthorized
    from zope.security.interfaces import Unauthorized
    from zope.security.interfaces import IForbidden
    from zope.security.interfaces import Forbidden
    from zope.security.interfaces import IForbiddenAttribute
    from zope.security.interfaces import ForbiddenAttribute
except ImportError:
    pass
