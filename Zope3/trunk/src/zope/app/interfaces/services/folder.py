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

$Id: folder.py,v 1.9 2004/02/11 07:00:58 jim Exp $
"""
import zope.app.interfaces.services.registration 
import zope.app.interfaces.container
import zope.app.interfaces.services.service
import zope.schema
from zope.app.container.constraints import ContainerTypesConstraint
from zope.app.interfaces.services.registration \
     import IRegistrationManagerContainer
from zope.app.container.constraints import ItemTypePrecondition

class ISiteManagementFolder(
    zope.app.interfaces.services.registration.IRegistrationManagerContainer,
    zope.app.interfaces.container.IContainer,
    ):
    """Component and component registration containers."""

    __parent__ = zope.schema.Field(
        constraint = ContainerTypesConstraint(
            zope.app.interfaces.services.service.ISiteManager,
            IRegistrationManagerContainer,
            ),
        )

class ISiteManagementFolders(
    zope.app.interfaces.container.IContainer,
    zope.app.interfaces.services.service.IComponentManager,
    ):
    """A collection of ISiteManagementFolder objects.

    An ISiteManagementFolders object supports simple containment as
    well as package query and lookup.
    
    """
