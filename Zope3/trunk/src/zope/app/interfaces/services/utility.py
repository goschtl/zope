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

$Id: utility.py,v 1.2 2003/03/21 21:02:19 jim Exp $
"""

from zope.app.interfaces.services.configuration import IComponentConfiguration
from zope.app.component.interfacefield import InterfaceField
from zope.app.security.permission import PermissionField
from zope.schema import BytesLine, TextLine
from zope.app.interfaces.services.configuration import IUseConfigurable
from zope.app.interfaces.services.configuration import ComponentPath

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
