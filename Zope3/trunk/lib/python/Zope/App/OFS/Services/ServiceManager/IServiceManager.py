##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""

$Id: IServiceManager.py,v 1.9 2002/12/18 20:23:05 stevea Exp $
"""
from Zope.ComponentArchitecture.IServiceService import IServiceService
from Zope.App.OFS.Services.ConfigurationInterfaces \
        import INameComponentConfigurable
from IComponentManager import IComponentManager
from Interface.Attribute import Attribute

class IServiceManager(IServiceService, IComponentManager,
                      INameComponentConfigurable):
    """Service Managers act as containers for Services.

    If a Service Manager is asked for a service, it checks for those it
    contains before using a context based lookup to find another service
    manager to delegate to.  If no other service manager is found they defer
    to the ComponentArchitecture ServiceManager which contains file based
    services.
    """

    Packages = Attribute("Package container")
