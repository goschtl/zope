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

$Id: interfaces.py,v 1.1 2004/03/11 22:05:01 srichter Exp $
"""
from zope.app.component.interfacefield import InterfaceField
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.interfaces.services.registration import IComponentRegistration
from zope.app.interfaces.services.registration import IRegisterable
from zope.app.interfaces.services.registration import ComponentPath
from zope.component.interfaces import IUtilityService
from zope.schema import TextLine

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


class ILocalUtilityService(IUtilityService):
    """Local utility service interface.

    Methods which must be implemented by a local utility service to
    allow views to retrieve sufficient information from the service.
    """
    
    def getLocalUtilitiesFor(interface):
        """Returns all active (registered is not enough) utilities that are
        directly registered with this utility service.

        An empty list is returned, if no local utilities for this interface
        were found. If the interface is None, all utilities will be retruned.
        """ 

    def getRegisteredMatching(interface=None, name=None):
        """Return the registered utilities.

        The return value is an iterable object for which each item
        is a three-element tuple:

        - provided interface

        - name

        - registration stack

        One item is present for each registration.

        If interface is None, all registered registrations are returned.
        Otherwise, only registrations that provide the given interface
        are returned.

        Also, if name is provided and is contained in the name of the
        registered utility, we use that to filter the returned values.
        """
