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

$Id: proxy.py,v 1.2 2002/12/25 14:15:21 jim Exp $
"""

from zope.security._proxy import getObject, getChecker
from zope.security._proxy import _Proxy as Proxy
from zope.security.checker import ProxyFactory, Checker as _trustedChecker

def trustedRemoveSecurityProxy(object):
    if ((type(object) is Proxy) and
        isinstance(getChecker(object), _trustedChecker)
        ):
        return getObject(object)

    return object


def getTestProxyItems(proxy):
    """Try to get checker names and permissions for testing

    If this succeeds, a sorted sequence of items is returned,
    otherwise, None is retirned.
    """
    checker = getChecker(proxy)
    func = checker.getPermission_func()
    dict = getattr(func, '__self__', None)
    if dict is None:
        return None
    items = dict.items()
    items.sort()
    return items
