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
"""Interfaces for folders.

$Id: folder.py,v 1.10 2004/03/03 10:38:46 philikon Exp $
"""
import zope.app.interfaces.services.registration 
import zope.app.container.interfaces
import zope.app.interfaces.services.service
import zope.schema
from zope.app.container.constraints import ContainerTypesConstraint
from zope.app.interfaces.services.registration \
     import IRegistrationManagerContainer
from zope.app.container.constraints import ItemTypePrecondition

class ISiteManagementFolder(
    zope.app.interfaces.services.registration.IRegistrationManagerContainer,
    zope.app.container.interfaces.IContainer,
    ):
    """Component and component registration containers."""

    __parent__ = zope.schema.Field(
        constraint = ContainerTypesConstraint(
            zope.app.interfaces.services.service.ISiteManager,
            IRegistrationManagerContainer,
            ),
        )

class ISiteManagementFolders(
    zope.app.container.interfaces.IContainer,
    zope.app.interfaces.services.service.IComponentManager,
    ):
    """A collection of ISiteManagementFolder objects.

    An ISiteManagementFolders object supports simple containment as
    well as package query and lookup.
    
    """
