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
"""General exceptions that wish they were standard exceptions

These exceptions are so general purpose that they don't belong in Zope
application-specific packages.

$Id: __init__.py,v 1.2 2002/12/25 14:13:38 jim Exp $
"""

from zope.exceptions._zope_error import ZopeError
from zope.exceptions.unauthorized import Unauthorized
from zope.exceptions._notfounderror import NotFoundError
from zope.exceptions._forbidden import Forbidden, ForbiddenAttribute
from zope.exceptions._duplicate import DuplicationError
