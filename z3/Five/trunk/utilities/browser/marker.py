##############################################################################
#
# Copyright (c) 2004, 2005 Zope Corporation and Contributors.
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
"""Marker utility views

$Id$
"""
from zope.app import zapi

from Products.Five.utilities.interfaces import IMarkerUtility


class EditView:

    """Marker interface edit view.
    """

    def __init__(self, context, request):
        self.utility = zapi.getUtility(IMarkerUtility)
        self.context = context
        self.request = request
        self.processForm()

        self.name = ''
        if request:
            path = request.environ['PATH_INFO'].split('/')
            self.name = path[-1]

        self.context_url = self.context.absolute_url()

    def add(self):
        return self.request.get('add', ())

    def name(self):
        return self.name

    def _getLinkToInterfaceDetailsView(self, interfaceName):
        return (self.context_url +
            '/views-details.html?iface=%s&type=zope.publisher.interfaces.browser.IBrowserRequest' % interfaceName)

    def _getNameLinkDicts(self, interfaceNames):
        return [dict(name=name,
                     link=self._getLinkToInterfaceDetailsView(name))
                for name in interfaceNames]

    def getAvailableInterfaceNames(self):
        return self._getNameLinkDicts(
            self.utility.getAvailableInterfaceNames(self.context))

    def getDirectlyProvidedNames(self):
        return self._getNameLinkDicts(
            self.utility.getDirectlyProvidedNames(self.context))

    def getInterfaceNames(self):
        return self._getNameLinkDicts(
            self.utility.getInterfaceNames(self.context))

    def processForm(self):
        # this could return errors
        ifaces = self.request.get('add', ()), self.request.get('remove', ())
        add, remove = [self.utility.dottedToInterfaces(self.context, seq) for seq in ifaces]
        self.utility.update(self.context, add=add, remove=remove)
