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
"""Locale Menu Service interfaces

$Id: menu.py,v 1.4 2004/03/02 17:40:50 philikon Exp $
"""
from zope.schema import Bool
from zope.app.publisher.interfaces.browser import \
     IBrowserMenu, IBrowserMenuService

class ILocalBrowserMenu(IBrowserMenu):
    """A local menu. Local menus can inherit menu entries from menus with the
    same name that are higher up the chain."""

    inherit = Bool(
        title=u"Inherit Items",
        description=u"If true, this menu will inherit menu items from menus"
                    u"higher up.",
        default=True,
        required=True)


class ILocalBrowserMenuService(IBrowserMenuService):
    """A persistent (local) browser menu service that can be fully managed.

    It is very useful to think about locally defined and inherited menus for
    local menu services. For this reason we provide several methods that allow
    specifically to query only locally or look through the entire path.
    """

    def getAllLocalMenus():
        """Returns a list of all local menus."""

    def getLocalMenu(menu_id):
        """Get a local menu by id.

        If there is no such menu found locally, this method needs to raise a
        ComponentLookupError.
        """

    def queryLocalMenu(menu_id, default=None):
        """Get a local menu by id.

        If no menu was found, the default value is returned.
        """

    def getInheritedMenu(menu_id, canBeLocal=False):
        """Tries to get the first available menu.

        If canBeLocal is True, then it also looks locally for a matching
        menu. This method should return a ComponentLookupError, if the menu
        was not found.
        """

    def queryInheritedMenu(menu_id, canBeLocal=False, default=None):
        """Tries to get the first available menu.

        If canBeLocal is True, then it also looks locally for a matching
        menu. If no menu was ound, default is returned.
        """


