##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
$Id: ComponentConfigURL.py,v 1.2 2002/12/12 11:32:31 mgedmin Exp $
"""

from Zope.ComponentArchitecture import getView
from Zope.App.Traversing import traverse, locationAsUnicode
from Zope.Proxy.ProxyIntrospection import removeAllProxies

__metaclass__ = type

class ComponentConfigURL:
    """View mixin that provides an absolute componentURL for
    Component configurations
    """

    def componentPath(self):
        return locationAsUnicode(self.context.componentPath)

    def componentURL(self):
        ob = traverse(self.context, self.context.componentPath)
        return str(getView(ob, 'absolute_url', self.request))


__doc__ = ComponentConfigURL.__doc__ + __doc__
