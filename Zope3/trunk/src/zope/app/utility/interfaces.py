##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Interfaces pertaining to local utilities.

$Id: interfaces.py,v 1.4 2004/04/17 14:33:42 srichter Exp $
"""
from zope.app.component.interfacefield import InterfaceField
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.registration.interfaces import IComponentRegistration
from zope.app.registration.interfaces import IRegisterable
from zope.app.registration.interfaces import IRegistry
from zope.app.registration.interfaces import ComponentPath
from zope.schema import TextLine
import zope.component.interfaces

class ILocalUtilityService(
        zope.component.interfaces.IUtilityService,
        IRegistry,
        ):
    """Local Utility Service
    """

class IUtilityRegistration(IComponentRegistration):
    """Utility registration object.

    This is keyed off name (which may be empty) and interface.  It
    overrides componentPath (to make it readonly); it also inherits a
    getComponent() method.
    """

    name = TextLine(
        title=_("Register As"),
        description=_("The name that is registered"),
        readonly=True,
        required=True,
        )

    interface = InterfaceField(
        title = _("Provided interface"),
        description = _("The interface provided by the adapter"),
        readonly = True,
        required = True,
        )

    componentPath = ComponentPath(
        title=_("Component path"),
        description=_("The physical path to the component"),
        required=True,
        readonly=True,
        )

class ILocalUtility(IRegisterable):
    """Local utility marker.

    A marker interface that indicates that a component can be used as
    a local utility.

    Utilities should usually also declare they implement
    IAttributeAnnotatable, so that the standard adapter to
    IRegistered can be used; otherwise, they must provide
    another way to be adaptable to IRegistered.
    """
