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
"""Interfaces for packages.

$Id: folder.py,v 1.3 2003/03/23 18:04:26 jim Exp $
"""

from zope.app.interfaces.container import IAdding, IContainer
from zope.app.interfaces.services.service import IComponentManager
from zope.interface import Interface

class INoConfigurationManagerError(Interface):
    """No configuration manager error
    """
    

class NoConfigurationManagerError(Exception):
    """No configuration manager

    There is no configuration manager in a site-management folder, or
    an operation would result in no configuration manager in a
    site-management folder.

    """

    __implements__ = INoConfigurationManagerError

class ISiteManagementFolder(IContainer):
    """Component and component configuration containers."""

class ISiteManagementFolders(IContainer, IComponentManager):
    """A collection of ISiteManagementFolder objects.

    An ISiteManagementFolders object supports simple containment as
    well as package query and lookup.
    
    """

    def getConfigurationManager():
        """get a configuration manager

        Find a configuration manager.  Clients can get the
        configuration manager without knowing it's name. Normally,
        folders have one configuration manager. If there is more than
        one, this method willl return one; which one is undefined.

        An error is raised if no configuration manager can be found.
        """

class ISiteManagementFolderAdding(IAdding):
    """A special package that is not content but is similar to a folder.
    
    The SiteManagementFolder Adding is special, since it is not part
    of the content namespace, but has a similar functionality as a
    Folder. Therefore there are views that overlap; this interface was
    created so that there are no configuration conflicts.

    """
