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

$Id: IServiceManager.py,v 1.3 2002/06/12 19:39:29 bwarsaw Exp $
"""
from Interface import Interface
from Zope.ComponentArchitecture.IServiceManager import IServiceManager as \
  IGlobalServiceManager
  # XXX fix once this package is changed to LocalServiceManager
from Zope.App.OFS.Container.IContainer import IContainer

class IServiceManager(IContainer, IGlobalServiceManager):
    """Service Managers act as containers for Services.
    
    If a Service Manager is asked for a service, it checks for those it
    contains before using a context based lookup to find another service
    manager to delegate to.  If no other service manager is found they defer
    to the ComponentArchitecture ServiceManager which contains file based
    services.
    """

    def bindService(serviceName, serviceComponentName):
        """Provide a service implementation.

        If the named object implements IBindingAware, the wrapped object is
        notified as per that interface.
        """

    def unbindService(serviceName):
        """No longer provide a service implementation.

        If the named object implements IBindingAware, the wrapped object is
        notified as per that interface.
        """

    def getBoundService(name):
        """Retrieve a bound service implementation.

        Get the component currently bound to the named Service in this
        ServiceService.   Does not search context.
        """
