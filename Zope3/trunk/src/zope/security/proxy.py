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
"""

$Id: proxy.py,v 1.5 2003/05/20 20:28:50 jim Exp $
"""

from zope.security._proxy import getObject, getChecker
from zope.security._proxy import _Proxy as Proxy
from zope.security.checker import Checker as _trustedChecker

# This import represents part of the API for this module
from zope.security.checker import ProxyFactory

def trustedRemoveSecurityProxy(object):
    """Remove a security proxy if the proxy's checker came from a trusted source.

    The rational is that it's OK to do this since the caller is
    trusted and the proxy can always be recreated by callingt the
    proxy factory and getting back a proxy with the same checker.

    XXX More thought needs to be given to assuring this contact.
    
    """
    if ((type(object) is Proxy) and
        isinstance(getChecker(object), _trustedChecker)
        ):
        return getObject(object)

    return object


def getTestProxyItems(proxy):
    """Try to get checker names and permissions for testing

    If this succeeds, a sorted sequence of items is returned,
    otherwise, None is returned.
    """
    checker = getChecker(proxy)
    func = checker.getPermission_func()
    dict = getattr(func, '__self__', None)
    if dict is None:
        return None
    items = dict.items()
    items.sort()
    return items
