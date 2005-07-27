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
"""Not Found Error

$Id$
"""
from zope.interface.common.interfaces import IKeyError
from zope.interface import implements

class INotFoundError(IKeyError):
    pass

class NotFoundError(KeyError, LookupError):
    """A resource could not be found.

    This exception is deprecated.  It will, over time, be replaced
    with more specific exception types.

    Eventually, when this exception type is used as a base class, it
    will become an alias for LookupError.  Client code should not depend
    on it extnding KeyError.
    
    """
    implements(INotFoundError)
