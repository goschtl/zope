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

$Id: IServiceManager.py,v 1.4 2002/07/11 18:21:32 jim Exp $
"""
from Zope.ComponentArchitecture.IServiceService import IServiceService

from IComponentManager import IComponentManager

from Interface.Attribute import Attribute

class IServiceManager(IServiceService, IComponentManager):
    """Service Managers act as containers for Services.
    
    If a Service Manager is asked for a service, it checks for those it
    contains before using a context based lookup to find another service
    manager to delegate to.  If no other service manager is found they defer
    to the ComponentArchitecture ServiceManager which contains file based
    services.
    """

    Packages = Attribute("""Package container""")
    

    def bindService(service_directive):
        """Provide a service implementation.

        If the named object implements IBindingAware, the wrapped object is
        notified as per that interface.
        """

    def addService(service_directive):
        """Add a registered service, but displace another active component

        Register a service component, but don't make it active of
        there is already a registered component providing the service.

        """

    def unbindService(service_directive):
        """No longer provide a service implementation.

        If the named object implements IBindingAware, the wrapped object is
        notified as per that interface.
        """

    def disableService(service_type):
        """Make the service type inactive in this service manager.

        This doesn't unbind any services, but makes them all inactive.
        """

    def enableService(service_type, index):
        """Make the service type inactive in this service manager.

        This doesn't unbind any services, but makes them all inactive.
        """

    def getBoundService(name):
        """Retrieve a bound service implementation.

        Get the component currently bound to the named Service in this
        ServiceService.   Does not search context.
        """

    def getDirectives(service_type):
        """Get the directives registered for a service
        """

    def getBoundServiceTypes():
        """Get a sequence of the bound service types"""
