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
"""XMLRPC configuration code

$Id: metaConfigure.py,v 1.1 2002/06/16 18:40:22 srichter Exp $
"""

from Zope.Security.Proxy import Proxy
from Zope.Security.Checker \
     import InterfaceChecker, CheckerPublic, NamesChecker, Checker

from Zope.Configuration.Action import Action
from Zope.Configuration.Exceptions import ConfigurationError

from Zope.Publisher.XMLRPC.IXMLRPCPresentation import IXMLRPCPresentation

from Zope.App.ComponentArchitecture.metaConfigure \
     import defaultView as _defaultView, handler


class view(object):

    type = IXMLRPCPresentation

    def __init__(self, _context, factory=None, name=None, for_=None,
                 permission=None,
                 allowed_interface=None, allowed_attributes=None):

        if for_ is not None:
            for_ = _context.resolve(for_)
        self.for_ = for_
        
        if ((allowed_attributes or allowed_interface)
            and ((name is None) or not permission)):
            raise ConfigurationError(
                "Must use name attribute with allowed_interface or "
                "allowed_attributes"
                )

        if allowed_interface is not None:
            allowed_interface = _context.resolve(allowed_interface)

        self.factory = self._factory(_context, factory)
        self.name = name
        self.permission = permission
        self.allowed_attributes = allowed_attributes
        self.allowed_interface = allowed_interface
        self.methods = 0


    def method(self, _context, name, attribute, permission=None, layer=None):
        permission = permission or self.permission
        factory = self._methodFactory(self.factory, attribute, permission)
        self.methods += 1

        return [
            Action(
                discriminator = self._discriminator(name),
                callable = handler,
                args = self._args(name, factory),
                )
            ]


    def _factory(self, _context, factory):
        return map(_context.resolve, factory.strip().split())


    def _discriminator(self, name):
        return ('view', self.for_, name, self.type)


    def _args(self, name, factory):
        return ('Views', 'provideView',
                self.for_, name, self.type, factory)


    def _methodFactory(self, factory, attribute, permission):

        factory = factory[:]        
        
        if permission:
            if permission == 'Zope.Public':
                permission = CheckerPublic

            def methodView(context, request,
                         factory=factory[-1], attribute=attribute,
                         permission=permission):
                return Proxy(getattr(factory(context, request), attribute),
                             NamesChecker(__call__ = permission))

        else:

            def methodView(context, request,
                         factory=factory[-1], attribute=attribute):
                return getattr(factory(context, request), attribute)

        factory[-1] = methodView

        return factory


    def _proxyFactory(self, factory, checker):
        factory = factory[:]        

        def proxyView(context, request,
                      factory=factory[-1], checker=checker):

            view = factory(context, request)

            # We need this in case the resource gets unwrapped and
            # needs to be rewrapped
            view.__Security_checker__ = checker

            return view

        factory[-1] =  proxyView

        return factory


    def __call__(self):
        if self.name is None:
            return ()

        permission = self.permission
        allowed_interface = self.allowed_interface
        allowed_attributes = self.allowed_attributes
        factory = self.factory

        if permission:
            if permission == 'Zope.Public':
                permission = CheckerPublic
            
            if ((not allowed_attributes) and (allowed_interface is None)
                and (not self.methods)):
                allowed_attributes = self.default_allowed_attributes

            require={}
            for name in (allowed_attributes or '').split():
                require[name] = permission
            if allowed_interface:
                for name in allowed_interface.names(1):
                    require[name] = permission

            checker = Checker(require.get)

            factory = self._proxyFactory(factory, checker)

        return [
            Action(
                discriminator = self._discriminator(self.name),
                callable = handler,
                args = self._args(self.name, factory),
                )
            ]


def defaultView(_context, name, for_=None, **__kw):

    if __kw:
        actions = view(_context, name=name, for_=for_, **__kw)()
    else:
        actions = []

    if for_ is not None:
        for_ = _context.resolve(for_)

    type = IXMLRPCPresentation

    actions += [Action(
        discriminator = ('defaultViewName', for_, type, name),
        callable = handler,
        args = ('Views','setDefaultViewName', for_, type, name),
        )]

    return actions
