##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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
"""Browser Views for Skin Browser

$Id$
"""
__docformat__ = 'restructuredtext'
from zope.app import zapi
from zope.app.apidoc import component, utilities
from zope.traversing import api, browser

from lovely.skinbrowser import module

class Menu(object):
    """Menu View Helper Class"""

    def getMenuTitle(self, node):
        """Return the title of the node that is displayed in the menu."""
        if zapi.isinstance(node.context, module.View):
            return node.context.title
        return api.getName(node.context)

    def getMenuLink(self, node):
        """Return the HTML link of the node that is displayed in the menu."""
        obj = node.context
        if zapi.isinstance(obj, module.Skin):
            return '../Interface/%s/index.html' %api.getName(obj)
        elif zapi.isinstance(obj, module.Component):
            path = utilities.getPythonPath(obj.spec)
            return '../Interface/%s/index.html' %path
        elif zapi.isinstance(obj, module.View):
            return browser.absoluteURL(obj, self.request)

