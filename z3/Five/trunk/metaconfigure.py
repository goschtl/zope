##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Generic Components ZCML Handlers

$Id$
"""
from zope.component import getService, getServices
from zope.component.servicenames import Adapters
from provideinterface import provideInterface
from zope.app.security.permission import Permission
from zope.app.security.interfaces import IPermission
from types import ModuleType
from zope.interface import classImplements
from zope.configuration.exceptions import ConfigurationError
from zope.component import getUtility
from zope.app.security.interfaces import IPermission

# Zope 2 stuff
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

CheckerPublic = 'zope.Public'
CheckerPrivate = 'zope.Private'

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

class ContentDirective:

    def __init__(self, _context, class_):
        self.__class = class_
        if isinstance(self.__class, ModuleType):
            raise ConfigurationError('Content class attribute must be a class')
        self.__context = _context

    def implements(self, _context, interface):
        for interface in interface:
            _context.action(
                discriminator = (
                'five::directive:content', self.__class, object()),
                callable = classImplements,
                args = (self.__class, interface),
                )
            interface(_context, interface)

    def require(self, _context, permission=None,
                attributes=None, interface=None):
        """Require a the permission to access a specific aspect"""

        if not (interface or attributes):
            raise ConfigurationError("Nothing required")

        if interface:
            for i in interface:
                if i:
                    self.__protectByInterface(i, permission)
        if attributes:
            self.__protectNames(attributes, permission)

    def allow(self, _context, attributes=None, interface=None):
        """Like require, but with permission_id zope.Public"""
        return self.require(_context, CheckerPublic, attributes, interface)

    def __protectByInterface(self, interface, permission_id):
        "Set a permission on names in an interface."
        for n, d in interface.namesAndDescriptions(1):
            self.__protectName(n, permission_id)
        interface(self.__context, interface)

    def __protectName(self, name, permission_id):
        "Set a permission on a particular name."
        self.__context.action(
            discriminator = ('five:protectName', self.__class, name),
            callable = protectName,
            args = (self.__class, name, permission_id)
            )

    def __protectNames(self, names, permission_id):
        "Set a permission on a bunch of names."
        for name in names:
            self.__protectName(name, permission_id)

    def __call__(self):
        "Handle empty/simple declaration."
        return self.__context.action(
            discriminator = ('five:initialize:class', self.__class),
            callable = initializeClass,
            args = (self.__class,)
            )

def initializeClass(klass):
    InitializeClass(klass)

def _getSecurity(klass):
    # a Zope 2 class can contain some attribute that is an instance
    # of ClassSecurityInfo. Zope 2 scans through things looking for
    # an attribute that has the name __security_info__ first
    info = vars(klass)
    for k, v in info.items():
        if hasattr(v, '__security_info__'):
            return v
    # we stuff the name ourselves as __security__, not security, as this
    # could theoretically lead to name clashes, and doesn't matter for
    # zope 2 anyway.
    security = ClassSecurityInfo()
    setattr(klass, '__security__', security)
    return security

def protectName(klass, name, permission_id):
    security = _getSecurity(klass)
    # Zope 2 uses string, not unicode yet
    name = str(name)
    if permission_id == CheckerPublic:
        security.declarePublic(name)
    elif permission_id == CheckerPrivate:
        security.declarePrivate(name)
    else:
        permission = getUtility(IPermission, name=permission_id)
        # Zope 2 uses string, not unicode yet
        perm = str(permission.title)
        security.declareProtected(perm, name)
