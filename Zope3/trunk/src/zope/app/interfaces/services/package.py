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

$Id: package.py,v 1.3 2002/12/30 20:07:20 jeremy Exp $
"""

from zope.app.interfaces.container import IAdding, IContainer
from zope.app.interfaces.services.service import IComponentManager

class IPackage(IContainer):
    """Component and component configuration containers."""

class IPackages(IContainer, IComponentManager):
    """A collection of IPackage objects.

    An IPackages object supports simple containment as well as package
    query and lookup.
    """

class IPackageAdding(IAdding):
    """A special package that is not content but is similar to a folder.
    
    The Package Adding is special, since it is not part of the content
    namespace, but has a similar functionality as a Folder. Therefore
    there are views that overlap; this interface was created so that
    there are no configuration conflicts.
    """
