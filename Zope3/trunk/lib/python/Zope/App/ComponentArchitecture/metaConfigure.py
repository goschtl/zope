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

from Zope.Configuration.Exceptions import ConfigurationError
from Zope.Security.Proxy import Proxy
from Zope.ComponentArchitecture import getService, getServiceManager
from Zope.Configuration import namespace
from Interface import Interface
from Zope.Configuration.Action import Action

from Zope.Security.Proxy import Proxy
from Zope.Security.Checker \
     import InterfaceChecker, CheckerPublic, NamesChecker, Checker

from Zope.ComponentArchitecture.GlobalServiceManager \
     import UndefinedService

# I prefer the indirection (using getService and getServiceManager vs.
# directly importing the various services)  not only because it makes
# unit tests easier, but also because it reinforces that the services
# should always be obtained through the
# IPlacefulComponentArchitecture interface methods

# But these services aren't placeful! And we need to get at things that
# normal service clients don't need!   Jim



def handler(serviceName, methodName, *args, **kwargs):
    method=getattr(getService(None, serviceName), methodName)
    method(*args, **kwargs)

def managerHandler(methodName, *args, **kwargs):
    method=getattr(getServiceManager(None), methodName)
    method(*args, **kwargs)

def adapter(_context, factory, provides, for_=None, permission=None):
    if for_ is not None: for_ = _context.resolve(for_)
    provides = _context.resolve(provides)
    factory = map(_context.resolve, factory.split())

    if permission is not None:
        if permission == 'Zope.Public':
            permission = CheckerPublic
        checker = InterfaceChecker(provides, permission)
        factory.append(lambda c: Proxy(c, checker))

    return [
        Action(
            discriminator = ('adapter', for_, provides),
            callable = handler,
            args = ('Adapters', 'provideAdapter', for_, provides, factory),
            )
        ]

def utility(_context, provides, component=None, factory=None, permission=None):
    provides = _context.resolve(provides)

    if factory:
        if component:
            raise TypeError("Can't specify factory and component.")

        component = _context.resolve(factory)()
    else:
        component = _context.resolve(component)

    if permission is not None:
        if permission == 'Zope.Public':
            permission = CheckerPublic
        checker = InterfaceChecker(provides, permission)

        component = Proxy(component, checker)

    return [
        Action(
            discriminator = ('utility', provides),
            callable = handler,
            args = ('Utilities', 'provideUtility', provides, component),
            )
        ]

def factory(_context, component, id=None):
    if id is None:
        id = component
        
    component = _context.resolve(component)

    return [
        Action(
            discriminator = ('factory', id),
            callable = handler,
            args = ('Factories', 'provideFactory', id, component),
            )
        ]

def _checker(_context, permission, allowed_interface, allowed_attributes):
    if (not allowed_attributes) and (not allowed_interface):
        allowed_attributes = "__call__"

    if permission == 'Zope.Public':
        permission = CheckerPublic

    require={}
    for name in (allowed_attributes or '').split():
        require[name] = permission
    if allowed_interface:
        for name in _context.resolve(allowed_interface).names(1):
            require[name] = permission

    checker = Checker(require.get)

    return checker

def resource(_context, factory, type, name, layer='default',
             permission=None,
             allowed_interface=None, allowed_attributes=None):

    if ((allowed_attributes or allowed_interface)
        and (not permission)):
        raise ConfigurationError(
            "Must use name attribute with allowed_interface or "
            "allowed_attributes"
            )

    
    type = _context.resolve(type)
    factory = _context.resolve(factory)


    if permission:

        checker = _checker(_context, permission,
                           allowed_interface, allowed_attributes)

        def proxyResource(request, factory=factory, checker=checker):
            return Proxy(factory(request), checker)

        factory = proxyResource
    
    return [
        Action(
            discriminator = ('resource', name, type, layer),
            callable = handler,
            args = ('Resources','provideResource',
                    name, type, factory, layer),
            )
        ]

def view(_context, factory, type, name, for_=None, layer='default',
         permission=None, allowed_interface=None, allowed_attributes=None):


    if ((allowed_attributes or allowed_interface)
        and (not permission)):
        raise ConfigurationError(
            "Must use name attribute with allowed_interface or "
            "allowed_attributes"
            )


    if for_ is not None: for_ = _context.resolve(for_)
    type = _context.resolve(type)

    factory = map(_context.resolve, factory.strip().split())
    if not factory:
        raise ConfigurationError("No view factory specified.")

    if permission:

        checker = _checker(_context, permission,
                           allowed_interface, allowed_attributes)

        def proxyView(context, request, factory=factory[-1], checker=checker):
            return Proxy(factory(context, request), checker)

        factory[-1] = proxyView

    return [
        Action(
            discriminator = ('view', for_, name, type, layer),
            callable = handler,
            args = ('Views','provideView',for_, name, type, factory, layer),
            )
        ]

def defaultView(_context, type, name, for_=None, **__kw):

    if __kw:
        actions = view(_context, type=type, name=name, for_=for_, **__kw)
    else:
        actions = []

    if for_ is not None:
        for_ = _context.resolve(for_)
    type = _context.resolve(type)

    actions += [Action(
        discriminator = ('defaultViewName', for_, type, name),
        callable = handler,
        args = ('Views','setDefaultViewName', for_, type, name),
        )]

    return actions

def serviceType(_context, id, interface):
    return [
        Action(
            discriminator = ('serviceType', id),        
            callable = managerHandler,
            args = ('defineService', id, _context.resolve(interface)),
            )
        ]

def provideService(serviceType, component, permission):
    # This is needed so we can add a security proxy.
    # We have to wait till execution time so we can find out the interface.
    # Waaaa.

    service_manager = getServiceManager(None)

    if permission:
        
        for stype, interface in service_manager.getServiceDefinitions():
            if stype == serviceType:
                break
        else:
            raise UndefinedService(serviceType)

        if permission == 'Zope.Public':
            permission = CheckerPublic
    
        checker = InterfaceChecker(interface, permission)

        try:
            component.__Security_checker__ = checker
        except: # too bad exceptions aren't more predictable
            component = Proxy(component, checker)

    service_manager.provideService(serviceType, component)
    
def service(_context, serviceType, component=None, permission=None, factory=None):
    if factory:
        if component:
            raise TypeError("Can't specify factory and component.")

        component = _context.resolve(factory)()
    else:
        component = _context.resolve(component)

    return [
        Action(
            discriminator = ('service', serviceType),        
            callable = provideService,
            args = (serviceType, component, permission),
            )
        ]

def skin(_context, name, layers, type):
    type = _context.resolve(type)
    if ',' in layers:
        raise TypeError("Commas are not allowed in layer names.")

    layers = layers.strip().split()
    return [
        Action(
            discriminator = ('skin', name, type),
            callable = handler,
            args = ('Skins','defineSkin',name, type, layers)
            )
        ]

