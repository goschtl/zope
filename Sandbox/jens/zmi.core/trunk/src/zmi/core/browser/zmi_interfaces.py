##############################################################################
#
# Copyright (c) 2011 Zope Foundation and Contributors.
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
"""Marker interfaces adapter views.
"""

from Products.Five.utilities.interfaces import IMarkerInterfaces
from zmi.core.browser.base import ZMIView


class InterfacesView(ZMIView):
    """Marker interface view.
    """

    def __init__(self, context, request):
        super(InterfacesView, self).__init__(context, request)
        self.adapted = IMarkerInterfaces(context)
        self.context_url = self.context.absolute_url()

    def __call__(self):
        return self.index()

    def _getLinkToInterfaceDetailsView(self, interfaceName):
        return (self.context_url +
            '/views-details.html?iface=%s&type=zope.publisher.interfaces.browser.IBrowserRequest' % interfaceName)

    def _getNameLinkDicts(self, interfaceNames):
        return [dict(name=name,
                     link=self._getLinkToInterfaceDetailsView(name))
                for name in interfaceNames]

    def getInterfaceNames(self):
        return self._getNameLinkDicts(self.adapted.getInterfaceNames())

