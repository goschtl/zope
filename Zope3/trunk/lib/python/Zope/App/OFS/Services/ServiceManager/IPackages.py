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

from Zope.App.OFS.Container.IContainer import IContainer
from Zope.App.OFS.Services.ServiceManager.IComponentManager import IComponentManager

class IPackages(IContainer, IComponentManager):
    """Packages objects contain database packages

    They support simple containment as well as package query and lookup.
    """

doc = IPackages.__doc__ + """
$Id: IPackages.py,v 1.1 2002/07/11 18:21:32 jim Exp $
"""
    
