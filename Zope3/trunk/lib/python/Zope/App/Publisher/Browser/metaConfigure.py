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
"""Browser configuration code

$Id: metaConfigure.py,v 1.3 2002/06/13 23:15:43 jim Exp $
"""

from Zope.Security.Proxy import Proxy
from Zope.Security.Checker \
     import InterfaceChecker, CheckerPublic, NamesChecker, Checker

from Zope.Configuration.Action import Action
from Zope.Configuration.Exceptions import ConfigurationError

from Zope.Publisher.Browser.IBrowserPresentation import IBrowserPresentation

from Zope.App.ComponentArchitecture.metaConfigure \
     import defaultView as _defaultView, skin as _skin, handler

from Zope.App.PageTemplate.SimpleViewClass import SimpleViewClass

from Zope.App.Publisher.Browser.FileResource \
     import FileResourceFactory, ImageResourceFactory

def skin(_context, **__kw):
    return _skin(_context,
                 type='Zope.Publisher.Browser.IBrowserPresentation.',
                 **__kw)

class resource(object):

    type = IBrowserPresentation
    default_allowed_attributes = '__call__'

    def __init__(self, _context, factory=None, name=None, layer='default',
                 permission=None,
                 allowed_interface=None, allowed_attributes=None,
                 file=None, image=None):

        if ((allowed_attributes or allowed_interface)
            and ((name is None) or not permission)):
            raise ConfigurationError(
                "Must use name attribute with allowed_interface or "
                "allowed_attributes"
                )

        if allowed_interface is not None:
            allowed_interface = _context.resolve(allowed_interface)

        self.__file = file
        self.__image = image

        self.factory = self._factory(_context, factory)
        self.layer = layer
        self.name = name
        self.permission = permission
        self.allowed_attributes = allowed_attributes
        self.allowed_interface = allowed_interface
        self.pages = 0

    def _factory(self, _context, factory):
        if ((factory is not None)
            + (self.__file is not None)
            + (self.__image is not None)
            ) > 1:
            raise ConfigurationError(
                "Can't use more than one of factory, file, and image "
                "attributes for resource directives"
                )
            
        if factory is not None:
            return _context.resolve(factory)

        if self.__file is not None:
            return FileResourceFactory(_context.path(self.__file))

        if self.__image is not None:
            return FileResourceFactory(_context.path(self.__image))

        raise ConfigurationError(
            "At least one of the factory, file, and image "
            "attributes for resource directives must be specified"
            )
        

    def page(self, _context, name, attribute, permission=None, layer=None):

        permission = permission or self.permission

        factory = self._pageFactory(self.factory, attribute, permission)

        self.pages += 1

        if layer is None:
            layer = self.layer

        return [
            Action(
                discriminator = self._discriminator(name, layer),
                callable = handler,
                args = self._args(name, factory, layer),
                )
            ]

    def _discriminator(self, name, layer):
        return ('resource', name, self.type, layer)

    def _args(self, name, factory, layer):
        return ('Resources', 'provideResource',
                name, self.type, factory, layer)
        
    def _pageFactory(self, factory, attribute, permission):
        if permission:
            if permission == 'Zope.Public':
                permission = CheckerPublic

            def pageView(request,
                         factory=factory, attribute=attribute,
                         permission=permission):
                return Proxy(getattr(factory(request), attribute),
                             NamesChecker(__call__ = permission))

        else:

            def pageView(request,
                         factory=factory, attribute=attribute):
                return getattr(factory(request), attribute)

        return pageView

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
                and (not self.pages)):
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
                discriminator = self._discriminator(self.name, self.layer),
                callable = handler,
                args = self._args(self.name, factory, self.layer),
                )
            ]

    def _proxyFactory(self, factory, checker):
        def proxyView(request,
                      factory=factory, checker=checker):
            resource = factory(request)

            # We need this in case the resource gets unwrapped and needs to be rewrapped
            resource.__Security_checker__ = checker

            return Proxy(resource, checker)

        return proxyView

class view(resource):

    def __init__(self, _context, factory=None, name=None, for_=None,
                 layer='default',
                 permission=None,
                 allowed_interface=None, allowed_attributes=None,
                 template=None):

        if template:
            if name is None:
                raise ConfigurationError(
                    "Must specify name for template view")

            self.default_allowed_attributes = (
                '__call__ __getitem__ browserDefault')

            template = _context.path(template)

        self.template = template

        if for_ is not None:
            for_ = _context.resolve(for_)
        self.for_ = for_
        
        resource.__init__(self, _context, factory, name, layer,
                          permission, allowed_interface, allowed_attributes)


    def page(self, _context, name, attribute, permission=None, layer=None):
        if self.template:
            raise ConfigurationError(
                "Can't use page or defaultPage subdirectives for simple "
                "template views")
        return super(view, self).page(
            _context, name, attribute, permission, layer)

    def _factory(self, _context, factory):

        if self.template:
            
            if factory:
                raise ConfigurationError(
                    "Can't specify factory and template")

            return [SimpleViewClass(
                str(_context.path(self.template)),
                used_for = self.for_
                )]

        else:
            return map(_context.resolve, factory.strip().split())

    def _discriminator(self, name, layer):
        return ('view', self.for_, name, self.type, layer)

    def _args(self, name, factory, layer):
        return ('Views', 'provideView',
                self.for_, name, self.type, factory, layer)

    def _pageFactory(self, factory, attribute, permission):

        factory = factory[:]        
        
        if permission:
            if permission == 'Zope.Public':
                permission = CheckerPublic

            def pageView(context, request,
                         factory=factory[-1], attribute=attribute,
                         permission=permission):
                return Proxy(getattr(factory(context, request), attribute),
                             NamesChecker(__call__ = permission))

        else:

            def pageView(context, request,
                         factory=factory[-1], attribute=attribute):
                return getattr(factory(context, request), attribute)

        factory[-1] = pageView

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


def defaultView(_context, name, for_=None, **__kw):

    if __kw:
        actions = view(_context, name=name, for_=for_, **__kw)()
    else:
        actions = []

    if for_ is not None:
        for_ = _context.resolve(for_)

    type = IBrowserPresentation

    actions += [Action(
        discriminator = ('defaultViewName', for_, type, name),
        callable = handler,
        args = ('Views','setDefaultViewName', for_, type, name),
        )]

    return actions
