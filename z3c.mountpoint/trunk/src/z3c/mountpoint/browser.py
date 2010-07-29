##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
"""Browser code

$Id$
"""
__docformat__ = "reStructuredText"
from zope.app.publisher.browser import menu, menumeta
from zope.security.checker import CheckerPublic

from z3c.mountpoint import interfaces

def ObjectMenuItem(context, request):
    factory = menumeta.MenuItemFactory(
        menu.BrowserMenuItem,
        title=u'Object',
        action=context.objectName + '/@@SelectedManagementView.html',
        permission=CheckerPublic,
        order=2,
        _for=interfaces.IMountPoint)
    return factory(context, request)
