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

$Id: ViewMeta.py,v 1.4 2002/06/20 20:00:27 jim Exp $
"""

# XXX this will need to be refactored soon. :)

from Zope.Security.Proxy import Proxy
from Zope.Security.Checker \
     import CheckerPublic, NamesChecker, Checker

from Zope.Configuration.Action import Action
from Zope.Configuration.Exceptions import ConfigurationError

from Zope.Publisher.Browser.IBrowserPresentation import IBrowserPresentation
from Zope.Publisher.Browser.IBrowserView import IBrowserView
from Zope.Publisher.Browser.IBrowserPublisher import IBrowserPublisher

from Zope.App.ComponentArchitecture.metaConfigure \
     import defaultView as _defaultView, handler

from Zope.App.PageTemplate.SimpleViewClass import SimpleViewClass
from Zope.App.PageTemplate import ViewPageTemplateFile

from ResourceMeta import resource

class view(resource):

    __pages = None
    __default = None

    def __init__(self, _context, factory=None, name=None, for_=None,
                 layer='default',
                 permission=None,
                 allowed_interface=None, allowed_attributes=None,
                 template=None, class_=None):

        if class_ and factory:
            raise ConfigurationError("Can't specify a class and a factory")

            
        factory = factory or class_

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

        if name:
            self.__pages = {}


    def page(self, _context, name, attribute=None, permission=None,
             layer=None, template=None):


        if self.template:
            raise ConfigurationError(
                "Can't use page or defaultPage subdirectives for simple "
                "template views")


        if self.name:
            # Named view with pages.

            if layer is not None:
                raise ConfigurationError(
                    "Can't specify a separate layer for pages of named "
                    "templates.")
            
            if template is not None:
                template = _context.path(template)

            self.__pages[name] = attribute, permission, template
            if self.__default is None:
                self.__default = name

            return ()

        factory = self.factory

        if template is not None:
            attribute = attribute or '__template__'
            klass = factory[-1]
            klass = type(klass.__name__, (klass, object), {
                attribute:
                ViewPageTemplateFile(_context.path(template))
                })
            factory = factory[:]
            factory[-1] = klass

        return super(view, self).page(
            _context, name, attribute, permission, layer,
            factory=factory)

    def defaultPage(self, _context, name):
        if self.name:
            self.__default = name
            return ()

        return [Action(
            discriminator = ('defaultViewName', self.for_, self.type, name),
            callable = handler,
            args = ('Views','setDefaultViewName', self.for_, self.type, name),
            )]
        

    def _factory(self, _context, factory):

        if self.template:
            

            if factory:
                factory = map(_context.resolve, factory.strip().split())
                bases = (factory[-1], )
                klass = SimpleViewClass(
                    str(_context.path(self.template)),
                    used_for=self.for_, bases=bases
                    )
                factory[-1] = klass
                return factory
                
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

    def __call__(self):
        if not self.__pages:
            return super(view, self).__call__()

        # OK, we have named pages on a named view.
        # We'l lreplace the original class with a new subclass that
        # can traverse to the necessary pages. 

        require = {}

        factory = self.factory[:]
        klass = factory[-1]

        klassdict = {'_PageTraverser__pages': {},
                     '_PageTraverser__default': self.__default,
                     '__implements__':
                     (klass.__implements__, PageTraverser.__implements__),
                     }
        for name in self.__pages:
            attribute, permission, template = self.__pages[name] 
            if permission == 'Zope.Public':
                permission = CheckerPublic

            if attribute:
                require[attribute] = permission
            else:
                attribute = name
                require[attribute] = permission

            if template:
                klassdict[attribute] = ViewPageTemplateFile(template)

            klassdict['_PageTraverser__pages'][name] = attribute

        klass = type(klass.__name__,
                     (klass, PageTraverser, object),
                     klassdict)
        factory[-1] = klass
        self.factory = factory

        return super(view, self).__call__(require=require)


class PageTraverser:

    __implements__ = IBrowserPublisher

    def publishTraverse(self, request, name):
        return getattr(self, self._PageTraverser__pages[name])

    def browserDefault(self, request):
        return self, (self._PageTraverser__default, )



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



