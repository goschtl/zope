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

$Id: utility.py,v 1.6 2003/05/01 19:35:22 faassen Exp $
"""

from zope.app.interfaces.services.configuration import IComponentConfiguration
from zope.app.component.interfacefield import InterfaceField
from zope.schema import TextLine
from zope.app.interfaces.services.configuration import IUseConfigurable
from zope.app.interfaces.services.configuration import ComponentPath
from zope.component.interfaces import IUtilityService

class IUtilityConfiguration(IComponentConfiguration):
    """Utility configuration object.

    This is keyed off name (which may be empty) and interface.  It
    overrides componentPath (to make it readonly); it also inherits a
    getComponent() method.
    """

    name = TextLine(title=u"Name",
                    description=u"The name that is registered",
                    readonly=True,
                    required=True,
                    )

    interface = InterfaceField(
        title = u"Provided interface",
        description = u"The interface provided by the adapter",
        readonly = True,
        required = True,
        )

    componentPath = ComponentPath(
        title=u"Component path",
        description=u"The physical path to the component",
        required=True,
        readonly=True,
        )



class ILocalUtility(IUseConfigurable):
    """Local utility marker.

    A marker interface that indicates that a component can be used as
    a local utility.

    Utilities should usually also declare they implement
    IAttributeAnnotatable, so that the standard adapter to
    IUseConfiguration can be used; otherwise, they must provide
    another way to be adaptable to IUseConfiguration.
    """



class ILocalUtilityService(IUtilityService):
    """Local utility service interface.

    Methods which must be implemented by a local utility service to
    allow views to retrieve sufficient information from the service.
    """

    def getRegisteredMatching():
        """Return the registrations.

        The return value is an iterable object for which each item
        is a three-element tuple:

        - provided interface

        - name

        - configuration registry

        One item is present for each registration.
        """
