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

$Id: folder.py,v 1.7 2003/12/03 05:41:26 jim Exp $
"""

import zope.app.interfaces.services.registration 
import zope.app.interfaces.container
import zope.app.interfaces.services.service
from zope.app.interfaces.services.registration \
     import IRegistrationManagerContainer
from zope.app.container.constraints import ItemTypePrecondition

class ISiteManagementFolder(
    zope.app.interfaces.container.IContainer,
    zope.app.interfaces.services.registration.IRegistrationManagerContainer,
    ):
    """Component and component registration containers."""

    def __setitem__(name, object):
        """Add a registerable object
        """
    __setitem__.precondition = ItemTypePrecondition(
        zope.app.interfaces.services.registration.IRegisterable)

class ISiteManagementFolders(
    zope.app.interfaces.container.IContainer,
    zope.app.interfaces.services.service.IComponentManager,
    ):
    """A collection of ISiteManagementFolder objects.

    An ISiteManagementFolders object supports simple containment as
    well as package query and lookup.
    
    """
