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
"""Browser-Specific Publisher interfaces

$Id: browser.py,v 1.8 2003/09/24 17:22:06 sidnei Exp $
"""
from zope.app.component.interfacefield import InterfaceField
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.security.permission import PermissionField
from zope.interface import Interface
from zope.schema import TextLine, Text


class IBrowserMenuItem(Interface):
    """A menu item represents one view. These views might be conditioned
    (using a filter) or being selected to be the default view of the menu."""

    interface = InterfaceField(
        title=_('interface-component', "Interface"),
        description=_("Specifies the interface this menu item is for."),
        required=True)

    action = TextLine(
        title=_("The relative url to use if the item is selected"),
        description=_("The url is relative to the object the menu is being "
                      "displayed for."),
        required=True)

    title = TextLine(
        title=_("Title"),
        description=_("The text to be displayed for the menu item"),
        required=True)

    description = Text(
        title=_("A longer explanation of the menu item"),
        description=_("A UI may display this with the item or display it "
                      "when the user requests more assistance."),
        required=False)

    permission = PermissionField(
        title=_("The permission needed access the item"),
        description=_("This can usually be inferred by the system, however, "
                      "doing so may be expensive. When displaying a menu, "
                      "the system tries to traverse to the URLs given in "
                      "each action to determine whether the url is "
                      "accessible to the current user. This can be avoided "
                      "if the permission is given explicitly."),
        required=False)

    filter_string = TextLine(
        title=_("A condition for displaying the menu item"),
        description=_("The condition is given as a TALES expression. The "
                      "expression has access to the variables:\n"
                      "\n"
                      "context -- The object the menu is being displayed "
                      "for\n"
                      "\n"
                      "request -- The browser request\n"
                      "\n"
                      "nothing -- None\n"
                      "\n"
                      "The menu item will not be displayed if there is a \n"
                      "filter and the filter evaluates to a false value."),
        required=False)


class IBrowserMenu(Interface):
    """A menu can contain a set of views that a represented asa
    collective."""

    title = TextLine(
        title=_("Title"),
        description=_("A descriptive title for documentation purposes"),
        required=True)

    description = Text(
        title=_("A longer explanation of the menu"),
        description=_("A UI may display this with the item or display it "
                      "when the user requests more assistance."),
        required=False)

    usage = TextLine(
        title=_("The templates usage top-level variable"),
        description=_("See the usage documentation in the README.txt in the "
                      "zope/app/browser/skins directory. If a view is "
                      "associated with a menu item, the view will get its "
                      "usage from the menu the menu item is registered to."),
        required=False)

    def getMenuItems(object=None):
        """Get a list of all menu entries in the usual form:

        (action, title, description, filter, permission)

        If object is None, all items are returned.
        """


class IBrowserMenuService(Interface):

    def getAllMenuItems(menu_id, object):
        """Returns a list of all menu items.

        The output is a list/tuple of:
        (action, title, description, filter, permission)

        This allows us to make the getMenu() method much less
        implementation-specific.
        """

    def getMenu(menu_id, object, request):
        """Get a browser menu for an object and request

        Return a sequence of mapping objects with keys:

        title -- The menu item title

        description -- The item title

        action -- A (possibly relative to object) URL for the menu item.

        The entries returned are accessable to the current user and
        have passed any menu item filters, if any.
        """

    def getFirstMenuItem(menu_id, object, request):
        """Get the first browser menu item for an object and request

        Return a mapping object with keys:

        title -- The menu item title

        description -- The item title

        action -- A (possibly relative to object) URL for the menu item.

        The entry returned is accessable to the current user and
        has passed any menu item filters, if any.

        If no entry can be found, None is returned.
        """

    def getMenuUsage(self, menu_id):
        """Return the usage attribute of a specified menu."""


class IGlobalBrowserMenuService(IBrowserMenuService):
    """The global menu defines some additional methods that make it easier to
    setup the service (via ZCML for example)."""

    def menu(self, menu_id, title, description=u'', usage=u''):
        """Add a new menu to the service."""

    def menuItem(self, menu_id, interface, action, title,
                 description='', filter_string=None, permission=None):
        """Add a menu item to a specific menu."""

