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
"""
$Id: ServiceDirective.py,v 1.1 2002/07/11 18:21:32 jim Exp $
"""

__metaclass__ = type

from Persistence import Persistent
from Zope.Security.Checker import CheckerPublic, InterfaceChecker
from Zope.Security.Proxy import Proxy
from Zope.App.Traversing import traverse
from IServiceDirective import IServiceDirective

class ServiceDirective(Persistent):
    __doc__ = IServiceDirective.__doc__
    
    __implements__ = IServiceDirective

    def __init__(self, service_type, component_path, permission=None):
        self.service_type = service_type
        self.component_path = component_path
        if permission == 'Zope.Public':
            permission = CheckerPublic
            
        self.permission = permission

    def __repr__(self):
        return "service(%s, %s)" % (self.service_type, self.component_path)

    ############################################################
    # Implementation methods for interface
    # Zope.App.OFS.Services.ServiceManager.IServiceDirective.

    def getService(self, service_manager):
        
        service = getattr(self, '_v_service', None)
        if service is None:
            service = traverse(service_manager, self.component_path)
            if self.permission:
                if type(service) is Proxy:
                    service = removeSecurityProxy(service)

                interface = service_manager.getInterfaceFor(self.service_type)

                checker = InterfaceChecker(interface, self.permission)

                service = Proxy(service, checker)

            
            self._v_service = service


        return service

    getService.__doc__ = IServiceDirective['getService'].__doc__

    #
    ############################################################

    
__doc__ = ServiceDirective.__doc__  + __doc__

            
