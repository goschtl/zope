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

$Id: metaConfigure.py,v 1.4 2002/11/19 23:25:14 jim Exp $
"""

from Zope.Security.Proxy import Proxy
from Zope.Security.Checker \
     import InterfaceChecker, CheckerPublic, NamesChecker, Checker

from Zope.Configuration.INonEmptyDirective import INonEmptyDirective
from Zope.Configuration.ISubdirectiveHandler import ISubdirectiveHandler
from Zope.Configuration.Action import Action
from Zope.Configuration.Exceptions import ConfigurationError

from Zope.Publisher.XMLRPC.IXMLRPCPresentation import IXMLRPCPresentation

from Zope.App.ComponentArchitecture.metaConfigure \
     import defaultView as _defaultView, handler
from Interface import Interface


class view(object):
    '''This view class handles the directives for the XML-RPC Presentation'''

    __class_implements__ = INonEmptyDirective
    __implementes__ = ISubdirectiveHandler

    type = IXMLRPCPresentation

    def __init__(self, _context, name=None, factory=None, for_=None,
                 permission=None, allowed_interface=None,
                 allowed_methods=None):

        # Resolve and save the component these views are for
        if for_ is not None:
            for_ = _context.resolve(for_)
        self.for_ = for_
        
        if ((allowed_methods or allowed_interface)
            and ((name is None) or not permission)):
            raise ConfigurationError(
                "Must use name attribute with allowed_interface or "
                "allowed_methods"
                )

        if allowed_interface is not None:
            allowed_interface = _context.resolve(allowed_interface)

        self.factory = map(_context.resolve, factory.strip().split())
        self.name = name
        self.permission = permission
        self.allowed_methods = allowed_methods
        self.allowed_interface = allowed_interface
        self.methods = 0


    def method(self, _context, name, attribute, permission=None):
        permission = permission or self.permission
        # make a copy of the factory sequence, sinc ewe might modify it
        # specifically for this method.
        factory = self.factory[:]        

        # if a specific permission was specified for this method we have to
        # apply a new proxy.
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

        self.methods += 1

        return [
            Action(
                discriminator = ('view', self.for_, name, self.type),
                callable = handler,
                args = ('Views', 'provideView', self.for_, name, self.type,
                        factory),
                )
            ]


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
        allowed_methods = self.allowed_methods
        factory = self.factory[:]

        if permission:
            if permission == 'Zope.Public':
                permission = CheckerPublic
            
            if ((not allowed_methods) and (allowed_interface is None)
                and (not self.methods)):
                allowed_methods = self.default_allowed_methods

            require = {}
            for name in (allowed_methods or '').split():
                require[name] = permission
            if allowed_interface:
                for name in allowed_interface.names(1):
                    require[name] = permission

            checker = Checker(require.get)

            def proxyView(context, request,
                          factory=factory[-1], checker=checker):
                view = factory(context, request)
                # We need this in case the resource gets unwrapped and
                # needs to be rewrapped
                view.__Security_checker__ = checker
                return view

            factory[-1] =  proxyView

        actions = [
            Action(
            discriminator = ('view', self.for_, self.name, self.type),
            callable = handler,
            args = ('Views', 'provideView', self.for_, self.name,
                    self.type, factory),
            )
            ]
        if self.for_ is not None:
            actions.append
            (
                Action(
                discriminator = None,
                callable = handler,
                args = ('Interfaces', 'provideInterface',
                        self.for_.__module__+'.'+self.for_.__name__, self.for_)
                )
                )
        return actions        
               
