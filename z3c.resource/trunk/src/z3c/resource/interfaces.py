##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""
$Id$
"""
__docformat__ = 'restructuredtext'

from zope.interface import Interface
from zope.location.interfaces import ILocation
from zope.schema import Field
from zope.annotation.interfaces import IAttributeAnnotatable

from zope.app.container.constraints import containers
from zope.app.container.constraints import contains
from zope.app.container.constraints import ContainerTypesConstraint
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.interfaces import IContainer

RESOURCE_KEY = 'z3c.resource.IResource'


class IResourceItem(Interface):
    """Resource item inside a resource container."""

    containers('z3c.resource.interfaces.IResource')


class IResource(ILocation, IContainer):
    """Resource container."""

    contains(IResourceItem)


class IResourceTraversable(IAttributeAnnotatable):
    """Marker for component that can be adapted to resource.

    The resource container can be traversed within the /@@/, too.
    """
