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

from zope.app.interfaces.container import IContainer
from zope.app.interfaces.services.service import IComponentManager

class IPackages(IContainer, IComponentManager):
    """Packages objects contain database packages

    They support simple containment as well as package query and lookup.
    """

doc = IPackages.__doc__ + """
$Id: package.py,v 1.2 2002/12/25 14:13:02 jim Exp $
"""



"""XXX short summary goes here.

XXX longer description goes here.

$Id: package.py,v 1.2 2002/12/25 14:13:02 jim Exp $
"""

from zope.app.interfaces.container import IContainer

class IPackage(IContainer):
    """Component and component configuration containers.
    """




"""IPackageAdding

$Id: package.py,v 1.2 2002/12/25 14:13:02 jim Exp $
"""
from zope.app.interfaces.container import IAdding

class IPackageAdding(IAdding):
    """The Package Adding is special, since it is not part of the content
    namespace, but has a similar functionality as a Folder. Therefore there
    are views that overlap; this interface was created so that there are no
    configuration conflicts."""
