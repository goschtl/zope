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
$Id: ConnectionConfigURL.py,v 1.1 2002/12/09 15:26:42 ryzaja Exp $
"""

from Zope.ComponentArchitecture import getView
from Zope.App.Traversing import traverse

__metaclass__ = type

class ConnectionConfigURL:
    """A view that provides an absolute URL from context.componentPath"""

    def componentURL(self):
        ob = traverse(self.context, self.context.componentPath)
        return str(getView(ob, 'absolute_url', self.request))

__doc__ = ConnectionConfigURL.__doc__ + __doc__

