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
"""Generic Components ZCML Handlers

$Id: metaconfigure.py,v 1.5 2004/06/02 08:44:01 faassen Exp $
"""
from zope.component import getService, getServices
from zope.component.servicenames import Adapters
from provideinterface import provideInterface
from Products.Five.security.permission import Permission
from Products.Five.security.interfaces import IPermission

def handler(serviceName, methodName, *args, **kwargs):
    method=getattr(getService(serviceName), methodName)
    method(*args, **kwargs)

def managerHandler(methodName, *args, **kwargs):
    method=getattr(getServices(), methodName)
    method(*args, **kwargs)

def serviceType(_context, id, interface):
    _context.action(
        discriminator = ('serviceType', id),
        callable = managerHandler,
        args = ('defineService', id, interface),
        )

    if interface.__name__ not in ['IUtilityService']:
        _context.action(
            discriminator = None,
             callable = provideInterface,
             args = (interface.__module__+'.'+interface.getName(),
                     interface)
             )

def provideService(serviceType, component, permission):
    # XXX this can probably be eliminated and provideService can be used
    # directly
    service_manager = getServices()
    service_manager.provideService(serviceType, component)

def service(_context, serviceType, component=None, permission=None,
            factory=None):
    if factory:
        if component:
            raise TypeError("Can't specify factory and component.")

        component = factory()

    _context.action(
        discriminator = ('service', serviceType),
        callable = provideService,
        args = (serviceType, component, permission),
        )

def interface(_context, interface, type=None):
    _context.action(
        discriminator = None,
        callable = provideInterface,
        args = ('', interface, type)
        )

def adapter(_context, factory, provides, for_, permission=None, name=''):
    for_ = tuple(for_)

    # Generate a single factory from multiple factories:
    factories = factory
    if len(factories) == 1:
        factory = factories[0]
    elif len(factories) < 1:
        raise ValueError("No factory specified")
    elif len(factories) > 1 and len(for_) != 1:
        raise ValueError("Can't use multiple factories and multiple for")
    else:
        def factory(ob):
            for f in factories:
                ob = f(ob)
            return ob
        # Store the original factory for documentation
        factory.factory = factories[0]

    _context.action(
        discriminator = ('adapter', for_, provides, name),
        callable = handler,
        args = (Adapters, 'register',
                for_, provides, name, factory, _context.info),
        )
    _context.action(
        discriminator = None,
        callable = provideInterface,
        args = ('', provides)
               )
    if for_:
        for iface in for_:
            if iface is not None:
                _context.action(
                    discriminator = None,
                    callable = provideInterface,
                    args = ('', iface)
                    )

def utility(_context, provides, component=None, factory=None,
            permission=None, name=''):
    if factory:
        if component:
            raise TypeError("Can't specify factory and component.")
        component = factory()

    _context.action(
        discriminator = ('utility', provides, name),
        callable = handler,
        args = ('Utilities', 'provideUtility',
                provides, component, name),
        )
    _context.action(
        discriminator = None,
        callable = provideInterface,
        args = (provides.__module__ + '.' + provides.getName(), provides)
               )

def definePermission(_context, id, title, description=''):
    permission = Permission(id, title, description)
    utility(_context, IPermission, permission, name=id)
