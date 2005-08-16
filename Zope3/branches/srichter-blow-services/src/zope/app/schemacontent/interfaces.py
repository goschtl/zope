##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Content Component Definition and Instance Interfaces

$Id$
"""
from zope.app.container.interfaces import IAdding
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.publisher.interfaces.browser import IBrowserMenuItem
from zope.interface import Interface, Attribute
from zope.schema import TextLine, Bool, Choice


class IContentComponentMenuItem(IBrowserMenuItem):
    """This is a schema that specifies the information needed to create a menu
    item for the Content Component.

    This reflects mainly the IBrowserMenuItem interface, except that the
    interface's default is set to IAdding, which should be the usual case. I
    also had to add a menuId field that specifies the menu (obviously).

    If the 'create' attribute is set to True, then the necessary components
    will be created locally.
    """

    interface = Choice(
        title=_('interface-component', "Interface"),
        description=_("Specifies the interface this menu item is for."),
        vocabulary="Interfaces",
        default=IAdding,
        required=True)
    
    menuId = TextLine(
        title=_("Menu Id"),
        description=_("Specifies the menu this menu item will be added to."),
        default=u"add_content",
        required=True)

    create = Bool(
        title=_("Create Menu"),
        description=_("If set to True, the system will create a local Browser"
                      "local browser menu item for you. If this "
                      "option is set to False, the system will try to find "
                      "the next site manager that has a menu "
                      "with the specifed id. If no menu was found or the menu "
                      "is a global menu, then an error is created."),
        default=True,
        required=True)
                 
    def createMenuItem():
        """Create a menu item from the information in this object."""

    def removeMenuItem():
        """Remove the specified menu item."""


class IContentComponentDefinition(Interface):
    """Content Component Definitions describe simple single-schema based
    content components including their security declarations."""

    name = TextLine(
        title=_("Name of Content Component Type"),
        description=_("This is the name of the document type."),
        required=True)

    schema = Choice(
        title=_('schema-component', "Schema"),
        description=_("Specifies the schema that characterizes the document."),
        vocabulary="Interfaces",
        required=True)

    copySchema = Bool(
        title=_("Copy Schema"),
        description=_("If this field is set to True, a copied version of the "
                      "schema will be used in the Content Component "
                      "instance. This has the advantage that an existing "
                      "Content Component's schema is set in stone and can "
                      "never change, even when a mutable schema evolves. If "
                      "the value is False, then the Content Component's "
                      "can change (which is desirable in some cases - i.e. "
                      "during development.)"),
        default=True,
        required=True)

    permissions = Attribute(
        u"A dictionary that maps set/get permissions on the schema's"
        u"fields. Entries looks as follows: {fieldname:(set_perm, get_perm)}")


class IContentComponentInstance(Interface):
    """Interface describing a Content Component Instance"""

    __name__ = TextLine(
        title=_("Name of Content Component Type"),
        description=_("This is the name of the document type."),
        required=True)

    __schema__ = Choice(
        title=_('schema-component', "Schema"),
        description=_("Specifies the schema that characterizes the document."),
        vocabulary="Interfaces",
        required=True)
