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

#from zope.viewlet.interfaces import IViewletManager
#from zope.viewlet.manager import ViewletManagerBase
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IDefaultBrowserLayer



class IZSCPLayer(IBrowserRequest):
    """``Layer for ZSCP Website``"""



class ZSCP(IZSCPLayer, IDefaultBrowserLayer):
    """The `ZSCP` skin 
    
    This skin is based on IZSCPLayer and IDefaultBrowserLayer.
    and accessible via `++skin++ZSCP`.
    """


#class IHead(IViewletManager):
#    """Head viewlet manager."""
#
#
#class ICSS(IViewletManager):
#    """CSS viewlet manager."""
#
#
#class IJavaScript(IViewletManager):
#    """JavaScript viewlet manager."""
#
#
#class IMenuBar(IViewletManager):
#    """Menu bar viewlet manager used for top level section."""
#
#
#class IBreadcrumb(IViewletManager):
#    """Breadcrumb viewlet manager."""
#
#
#class ILeft(IViewletManager):
#    """Left viewlet manager."""
#
#
#class IRight(IViewletManager):
#    """Right viewlet manager."""
#
#
#
#class WeightOrderedViewletManager(ViewletManagerBase):
#
#    def sort(self, viewlets):
#        def getWeight(viewlet):
#            try:
#                return viewlet.weight
#            except:
#                return 0
#        return sorted(viewlets, lambda x, y: cmp(getWeight(x[1]), getWeight(y[1])))
