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
"""Helper functions for Proxies.

$Id: proxy.py,v 1.9 2004/02/20 20:42:12 srichter Exp $
"""
from zope.proxy import getProxiedObject
from zope.security._proxy import getChecker
from zope.security._proxy import _Proxy as Proxy
from zope.security.checker import TrustedCheckerBase

# This import represents part of the API for this module
from zope.security.checker import ProxyFactory

def trustedRemoveSecurityProxy(object):
    """Remove a security proxy if its checker came from a trusted source.

    The rationale is that it is OK to do this since the caller is
    trusted and the proxy can always be recreated by calling the
    proxy factory and getting back a proxy with the same checker.

    XXX More thought needs to be given to assuring this contract.
    """
    if ((type(object) is Proxy) and
        isinstance(getChecker(object), TrustedCheckerBase)
        ):
        return getProxiedObject(object)

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
