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

from zope.security.proxy import removeSecurityProxy

from zope.app import servicenames
from zope.app.interface import queryType

moduleProvides(IZAPI)
__all__ = tuple(IZAPI)

from zope.component import *

from zope.app.traversing.api import *
from zope.app.traversing.browser.absoluteurl import absoluteURL
from zope.app.exception.interfaces import UserError

name = getName

builtin_isinstance = isinstance
def isinstance(object, cls):
    """Test whether an object is an instance of a type.

    This works even if the object is security proxied:

      >>> class C1(object):
      ...     pass

      >>> c = C1()
      >>> isinstance(c, C1)
      True

      >>> from zope.security.checker import ProxyFactory
      >>> isinstance(ProxyFactory(c), C1)
      True

      >>> class C2(C1):
      ...     pass

      >>> c = C2()
      >>> isinstance(c, C1)
      True

      >>> from zope.security.checker import ProxyFactory
      >>> isinstance(ProxyFactory(c), C1)
      True
      
    """

    # The removeSecurityProxy call is OK here because it is *only*
    # being used for isinstance
    
    return builtin_isinstance(removeSecurityProxy(object), cls)
