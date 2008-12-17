##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
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
""" z3ext.layoutform interfaces

$Id$
"""
from zope import interface, schema
from zope.i18nmessageid import MessageFactory
from z3c.form.interfaces import IFormLayer
from z3ext.layout.interfaces import IPagelet

_ = MessageFactory('z3ext.layoutform')


class IAddAction(interface.Interface):
    """ add action """


class ISaveAction(interface.Interface):
    """ save action """


class ICancelAction(interface.Interface):
    """ cancel action """


class ILayoutFormLayer(IFormLayer):
    """ browser layer """


class IPageletFormView(interface.Interface):
    """ pagelet form view """


class IPageletBaseForm(IPagelet):
    """ Base interface for pagelet forms """


class IPageletForm(IPageletBaseForm):
    """Form mixin for pagelet implementation."""

    label = interface.Attribute('Form label')

    description = interface.Attribute('Form label')

    forms = interface.Attribute('Ordered list of managed forms')
    groups = interface.Attribute('Ordered list of managed groups')
    subforms = interface.Attribute('Ordered list of managed subforms')

    def updateForms():
        """Update pagelet subforms."""


class IPageletAddForm(IPageletForm):
    """Add form mixin for pagelet implementation."""

    formCancelMessage = interface.Attribute('Form cancel message')

    def nextURL():
        """ as next url use newly created content url """

    def cancelURL():
        """ cancel url """

    def nameAllowed():
        """Return whether names can be input by the user."""


class IPageletDisplayForm(IPageletBaseForm):
    """ Display form mixin """


class IPageletEditForm(IPageletForm):
    """Edit form mixin for pagelet implementation."""

    def nextURL():
        """ as next url use newly created content url """


class IPageletEditSubForm(IPageletBaseForm):
    """ Sub form mixin for pagelet implementation."""

    def executeActions(form):
        """Execute form actions."""


class IPageletSubform(interface.Interface):
    """ Subform """

    weight = schema.Int(
        title = u'Weight',
        description = u'Weight for order',
        default = 9999,
        required = False)

    def isAvailable():
        """If subform available."""

    def postUpdate():
        """Update form after manager form updated."""


class IAddButton(IAddAction):
    """ add button """


class ISaveButton(ISaveAction):
    """ save button """


class ICancelButton(ICancelAction):
    """ cancel button """
