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
# FOR A PARTICULAR PURPOSE
# 
##############################################################################
"""

Revision information:
$Id: IProxyIntrospection.py,v 1.2 2002/06/10 23:29:31 jim Exp $
"""

from Interface import Interface

class IProxyIntrospection(Interface):
    """Provides methods for indentifying proxies and extracting proxied objects
    """

    def removeProxy(obj):
        """Return the immediately proxied object.

        If obj is not a proxied object, return obj.

        Note that the object returned may still be a proxy, if there
        are multiple layers of proxy.
        """

    def removeAllProxies(obj):
        """Get the proxied oject with no proxies

        If obj is not a proxied object, return obj.

        The reurned object has no proxies.
        """

    def isProxy(obj):
        """Checkj whether the given object is a proxy
        """


