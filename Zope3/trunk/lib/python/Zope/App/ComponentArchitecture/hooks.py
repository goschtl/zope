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

$Id: hooks.py,v 1.3 2002/07/12 22:46:08 jim Exp $
"""
from Zope.ComponentArchitecture.IServiceService import IServiceService
from Zope.ComponentArchitecture.IServiceManagerContainer \
     import IServiceManagerContainer
from Zope.ComponentArchitecture.Exceptions import ComponentLookupError
from Zope.Proxy.ContextWrapper import getWrapperContainer, ContextWrapper
from Zope.ComponentArchitecture import getServiceManager
from Zope.ComponentArchitecture.Exceptions import ComponentLookupError
from Zope.ComponentArchitecture.GlobalServiceManager import serviceManager
from Zope.Proxy.ProxyIntrospection import removeAllProxies
from Zope.Security.Proxy import trustedRemoveSecurityProxy
    
def getServiceManager_hook(context):
    """
    context based lookup, with fallback to component architecture
    service manager if no service manager found within context
    """
    while context is not None:
        clean_context = removeAllProxies(context)

        # if the context is actually a service or service manager...
        if IServiceService.isImplementedBy(clean_context):
            return trustedRemoveSecurityProxy(context)
        
        if (IServiceManagerContainer.isImplementedBy(clean_context) and
            clean_context.hasServiceManager()
            ):
            return ContextWrapper(
                trustedRemoveSecurityProxy(context.getServiceManager()),
                context,
                name="++etc++Services",
                )
                                  
        context = getWrapperContainer(context)

    return serviceManager

def getNextServiceManager_hook(context):
    """if the context is a service manager or a placeful service, tries
    to return the next highest service manager"""

    # get this service manager
    sm = getServiceManager_hook(context)
    if sm is serviceManager:
        raise ComponentLookupError('service manager')

    # get the service manager container, which ought to be the context
    # contaioner.
    container = getWrapperContainer(sm)

    # But we're *really* paranoid, so we'll double check.
    while ((container is not None) and not 
           IServiceManagerContainer.isImplementedBy(
                      removeAllProxies(container))
           ):
        container = getWrapperContainer(container) # we should be

    # Now we need to step up so we can look for a service manager above.
    context = getWrapperContainer(container)

    # But we have to make sure we haven't got the same object..
    while (context is not None) and (context == container):
        context = getWrapperContainer(context)

    return getServiceManager_hook(context)
