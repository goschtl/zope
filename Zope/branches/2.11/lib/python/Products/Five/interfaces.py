##############################################################################
#
# Copyright (c) 2004, 2005 Zope Foundation and Contributors.
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
"""Five interfaces

$Id$
"""
from zope.interface.interfaces import IInterface

class IMenuItemType(IInterface):
    """Menu item type

    Menu item types are interfaces that define classes of
    menu items.
    """

# BBB 2006/05/01 -- to be removed after 12 months
import zope.deferredimport
zope.deferredimport.deprecated(
    "To get the default browser view of an object, use "
    "zope.app.publisher.browser.queryDefaultViewName. To "
    "define the default view of an object, use the "
    "browser:defaultView directive",
    IBrowserDefault = "Products.Five.bbb:IBrowserDefault",
    )
