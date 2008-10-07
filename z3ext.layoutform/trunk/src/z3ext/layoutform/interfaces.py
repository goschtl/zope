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
from zope import interface
from zope.i18nmessageid import MessageFactory
from z3c.form.interfaces import IFormLayer
from z3ext.layout.interfaces import IPagelet
from z3ext.statusmessage.interfaces import IMessage

_ = MessageFactory('z3ext')


class ILayoutFormLayer(IFormLayer):
    """ browser layer """


class IPageletFormView(IPagelet):
    """ pagelet form view """


class IPageletForm(IPagelet):
    """Form mixin for pagelet implementation."""

    label = interface.Attribute('Form label')

    description = interface.Attribute('Form label')


class IPageletAddForm(IPageletForm):
    """Add form mixin for pagelet implementation."""

    formCancelMessage = interface.Attribute('Form cancel message')

    def nextURL():
        """ as next url use newly created content url """

    def cancelURL():
        """ cancel url """

    def nameAllowed():
        """Return whether names can be input by the user."""


class IPageletEditForm(IPageletForm):
    """Edit form mixin for pagelet implementation."""

    def nextURL():
        """ as next url use newly created content url """


class IAddButton(interface.Interface):
    """ add button """


class ISaveButton(interface.Interface):
    """ save button """


class ICancelButton(interface.Interface):
    """ cancel button """


class IFormErrorStatusMessage(IMessage):
    """ form error status message """
