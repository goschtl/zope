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
"""Configuration handlers for 'tools' directive.

$Id: metaconfigure.py,v 1.1 2004/03/21 16:02:18 srichter Exp $
"""
from zope.publisher.interfaces.browser import IBrowserRequest, IBrowserPublisher
from zope.app.component.metaconfigure import view, interface as ifaceDirective

from zope.app.site.interfaces import ISiteManager
from tools import UtilityToolsViewFactory, IUtilityToolsView, IToolType

def tool(_context, interface, folder="tools", title=None, description=None):

    factory = UtilityToolsViewFactory(interface, folder, title, description)
    name = "manage" + interface.getName() + "Tool.html"
    permission = 'zope.ManageContent'


    ifaceDirective(_context, interface, IToolType)

    view(_context, [factory], IBrowserRequest, name, [ISiteManager],
         permission=permission,
         allowed_interface=[IUtilityToolsView, IBrowserPublisher],
         allowed_attributes=['__call__', '__getitem__'])


