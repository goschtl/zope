##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""
$Id$
"""

__docformat__ = "reStructuredText"

from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.viewlet.interfaces import IViewletManager
from zope.viewlet.manager import ViewletManagerBase



class IZSCPLayer(IBrowserRequest):
    """``Layer for ZSCP Website``"""



class ZSCP(IZSCPLayer, IDefaultBrowserLayer):
    """The `ZSCP` skin 
    
    This skin is based on IZSCPLayer and IDefaultBrowserLayer.
    and accessible via `++skin++ZSCP`.
    """


class ILeft(IViewletManager):
    """Left viewlet manager."""


class WeightOrderedViewletManager(ViewletManagerBase):

    def sort(self, viewlets):
        def getWeight(viewlet):
            try:
                return viewlet.weight
            except:
                return 0
        return sorted(viewlets, lambda x, y: cmp(getWeight(x[1]), getWeight(y[1])))
