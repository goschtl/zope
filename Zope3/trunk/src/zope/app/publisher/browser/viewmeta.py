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
"""Browser configuration code

$Id$
"""
import os

from zope.component.exceptions import ComponentLookupError
from zope.configuration.exceptions import ConfigurationError
from zope.exceptions import NotFoundError
from zope.interface import implements, classImplements, Interface
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.exceptions import NotFoundError
from zope.security.checker import CheckerPublic, Checker
from zope.security.checker import defineChecker
from zope.configuration.exceptions import ConfigurationError
from zope.app.component.interface import provideInterface
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.app.publisher.browser import BrowserView
from zope.app import zapi
from zope.app.component.metaconfigure import handler
from zope.app.pagetemplate.simpleviewclass import SimpleViewClass
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.publisher.browser import BrowserView
from zope.app.publisher.browser.globalbrowsermenuservice import \
     menuItemDirective, globalBrowserMenuService
from zope.app.security.permission import checkPermission



# There are three cases we want to suport:
#
# Named view without pages (single-page view)
#
#     <browser:page
#         for=".IContact.IContactInfo."
#         name="info.html" 
#         template="info.pt"
#         class=".ContactInfoView."
#         permission="zope.View"
#         />
#
# Unamed view with pages (multi-page view)
#
#     <browser:pages
#         for=".IContact."
#         class=".ContactEditView."
#         permission="ZopeProducts.Contact.ManageContacts"
#         >
# 
#       <browser:page name="edit.html"       template="edit.pt" />
#       <browser:page name="editAction.html" attribute="action" />
#       </browser:pages>
#
# Named view with pages (add view is a special case of this)
#
#        <browser:view
#            name="ZopeProducts.Contact"
#            for="Zope.App.OFS.Container.IAdding."
#            class=".ContactAddView."
#            permission="ZopeProducts.Contact.ManageContacts"
#            >
#
#          <browser:page name="add.html"    template="add.pt" />
#          <browser:page name="action.html" attribute="action" />
#          </browser:view>

# We'll also provide a convenience directive for add views:
#
#        <browser:add
#            name="ZopeProducts.Contact"
#            class=".ContactAddView."
#            permission="ZopeProducts.Contact.ManageContacts"
#            >
#
#          <browser:page name="add.html"    template="add.pt" />
#          <browser:page name="action.html" attribute="action" />
#          </browser:view>

# page

def page(_context, name, permission, for_,
         layer='default', template=None, class_=None,
         allowed_interface=None, allowed_attributes=None,
         attribute='__call__', menu=None, title=None, 
         ):

    try:
        s = zapi.getGlobalService(zapi.servicenames.Presentation)
    except ComponentLookupError, err:
        pass

    _handle_menu(_context, menu, title, [for_], name, permission)

    required = {}

    permission = _handle_permission(_context, permission)

    if not (class_ or template):
        raise ConfigurationError("Must specify a class or template")

    if attribute != '__call__':
        if template:
            raise ConfigurationError(
                "Attribute and template cannot be used together.")

        if not class_:
            raise ConfigurationError(
                "A class must be provided if attribute is used")

    if template:
        template = os.path.abspath(str(_context.path(template)))
        if not os.path.isfile(template):
            raise ConfigurationError("No such file", template)
        required['__getitem__'] = permission

    if class_:
        if attribute != '__call__':
            if not hasattr(class_, attribute):
                raise ConfigurationError(
                    "The provided class doesn't have the specified attribute "
                    )
        if template:
            # class and template
            new_class = SimpleViewClass(
                template, bases=(class_, ))
        else:
            if not hasattr(class_, 'browserDefault'):
                cdict = {
                    'browserDefault':
                    lambda self, request: (getattr(self, attribute), ())
                    }
            else:
                cdict = {}

            cdict['__page_attribute__'] = attribute
            new_class = type(class_.__name__,
                             (class_, simple,),
                             cdict)

        if hasattr(class_, '__implements__'):
            classImplements(new_class, IBrowserPublisher)

    else:
        # template
        new_class = SimpleViewClass(template)

    for n in (attribute, 'browserDefault', '__call__', 'publishTraverse'):
        required[n] = permission

    _handle_allowed_interface(_context, allowed_interface, permission,
                              required)
    _handle_allowed_attributes(_context, allowed_interface, permission,
                               required)

    _handle_for(_context, for_)

    defineChecker(new_class, Checker(required))

    _context.action(
        discriminator = ('view', for_, name, IBrowserRequest, layer),
        callable = handler,
        args = (zapi.servicenames.Presentation, 'provideAdapter',
                IBrowserRequest, new_class, name, [for_], Interface, layer,
                _context.info),
        )


# pages, which are just a short-hand for multiple page directives.

# Note that a class might want to access one of the defined
# templates. If it does though, it should use getView.

class pages:

    def __init__(self, _context, for_, permission,
                 layer='default', class_=None,
                 allowed_interface=None, allowed_attributes=None,
                 ):
        self.opts = dict(for_=for_, permission=permission,
                         layer=layer, class_=class_,
                         allowed_interface=allowed_interface,
                         allowed_attributes=allowed_attributes,
                         )

    def page(self, _context, name, attribute='__call__', template=None,
             menu=None, title=None):
        return page(_context,
                    name=name,
                    attribute=attribute,
                    template=template,
                    menu=menu, title=title,
                    **(self.opts))

    def __call__(self):
        return ()

# view (named view with pages)

# This is a different case. We actually build a class with attributes
# for all of the given pages.

class view:

    default = None

    def __init__(self, _context, for_, permission,
                 name='', layer='default', class_=None,
                 allowed_interface=None, allowed_attributes=None,
                 menu=None, title=None, provides=Interface,
                 ):

        _handle_menu(_context, menu, title, [for_], name, permission)

        permission = _handle_permission(_context, permission)

        self.args = (_context, name, for_, permission, layer, class_,
                     allowed_interface, allowed_attributes)

        self.pages = []
        self.menu = menu
        self.provides = provides

    def page(self, _context, name, attribute=None, template=None):
        if template:
            template = os.path.abspath(_context.path(template))
            if not os.path.isfile(template):
                raise ConfigurationError("No such file", template)
        else:
            if not attribute:
                raise ConfigurationError(
                    "Must specify either a template or an attribute name")

        self.pages.append((name, attribute, template))
        return ()

    def defaultPage(self, _context, name):
        self.default = name
        return ()

    def __call__(self):
        (_context, name, for_, permission, layer, class_,
         allowed_interface, allowed_attributes) = self.args

        required = {}

        cdict = {}
        pages = {}

        for pname, attribute, template in self.pages:
            try:
                s = zapi.getGlobalService(zapi.servicenames.Presentation)
            except ComponentLookupError, err:
                pass

            if template:
                cdict[pname] = ViewPageTemplateFile(template)
                if attribute and attribute != name:
                    cdict[attribute] = cdict[pname]
            else:
                if not hasattr(class_, attribute):
                    raise ConfigurationError("Undefined attribute",
                                             attribute)

            attribute = attribute or pname
            required[pname] = permission

            pages[pname] = attribute

        # This should go away, but noone seems to remember what to do. :-(
        if hasattr(class_, 'publishTraverse'):

            def publishTraverse(self, request, name,
                                pages=pages, getattr=getattr):

                if name in pages:
                    return getattr(self, pages[name])
                view = zapi.queryView(self, name, request)
                if view is not None:
                    return view

                m = class_.publishTraverse.__get__(self)
                return m(request, name)

        else:
            def publishTraverse(self, request, name,
                                pages=pages, getattr=getattr):

                if name in pages:
                    return getattr(self, pages[name])
                view = zapi.queryView(self, name, request)
                if view is not None:
                    return view

                raise NotFoundError(self, name, request)

        cdict['publishTraverse'] = publishTraverse

        if not hasattr(class_, 'browserDefault'):
            if self.default or self.pages:
                default = self.default or self.pages[0][0]
                cdict['browserDefault'] = (
                    lambda self, request, default=default:
                    (self, (default, ))
                    )
            elif providesCallable(class_):
                cdict['browserDefault'] = (
                    lambda self, request: (self, ())
                    )

        if class_ is not None:
            bases = (class_, simple)
        else:
            bases = (simple,)

        try:
            cname = str(name)
        except:
            cname = "GeneratedClass"

        newclass = type(cname, bases, cdict)

        for n in ('publishTraverse', 'browserDefault', '__call__'):
            required[n] = permission

        _handle_allowed_interface(_context, allowed_interface, permission,
                                  required)
        _handle_allowed_attributes(_context, allowed_interface, permission,
                                   required)
        _handle_for(_context, for_)

        defineChecker(newclass, Checker(required))

        if self.provides is not None:
            _context.action(
                discriminator = None,
                callable = provideInterface,
                args = ('', self.provides)
                )

        _context.action(
            discriminator = ('view', for_, name, IBrowserRequest, layer,
                             self.provides),
            callable = handler,
            args = (zapi.servicenames.Presentation, 'provideAdapter',
                    IBrowserRequest, newclass, name, [for_],  self.provides,
                    layer, _context.info),
            )

def addview(_context, name, permission,
            layer='default', class_=None,
            allowed_interface=None, allowed_attributes=None,
            menu=None, title=None
            ):
    return view(_context, name,
                'zope.app.container.interfaces.IAdding',
                permission,
                layer, class_,
                allowed_interface, allowed_attributes,
                menu, title
                )

def defaultView(_context, name, for_=None):

    _context.action(
        discriminator = ('defaultViewName', for_, IBrowserRequest, name),
        callable = handler,
        args = (zapi.servicenames.Presentation,'setDefaultViewName',
                for_, IBrowserRequest,
                name),
        )

    if for_ is not None:
        _context.action(
            discriminator = None,
            callable = provideInterface,
            args = ('', for_)
            )
        

def _handle_menu(_context, menu, title, for_, name, permission):
    if menu or title:
        if not (menu and title):
            raise ConfigurationError(
                "If either menu or title are specified, they must "
                "both be specified.")

        if len(for_) != 1:
            raise ConfigurationError(
                "Menus can be specified only for single-view, not for "
                "multi-views.")
            
        return menuItemDirective(
            _context, menu, for_[0], '@@' + name, title,
            permission=permission)

    return []


def _handle_permission(_context, permission):
    if permission == 'zope.Public':
        permission = CheckerPublic

    return permission

def _handle_allowed_interface(_context, allowed_interface, permission,
                              required):
    # Allow access for all names defined by named interfaces
    if allowed_interface:
        for i in allowed_interface:
            _context.action(
                discriminator = None,
                callable = provideInterface,
                args = (None, i)
                )
            
            for name in i:
                required[name] = permission

def _handle_allowed_attributes(_context, allowed_attributes, permission,
                               required):
    # Allow access for all named attributes
    if allowed_attributes:
        for name in allowed_attributes:
            required[name] = permission

def _handle_for(_context, for_):
    if for_ is not None:
        _context.action(
            discriminator = None,
            callable = provideInterface,
            args = ('', for_)
            )        

class simple(BrowserView):
    implements(IBrowserPublisher)

    def publishTraverse(self, request, name):
        raise NotFoundError(self, name, request)

    def __call__(self, *a, **k):
        # If a class doesn't provide it's own call, then get the attribute
        # given by the browser default.

        attr = self.__page_attribute__
        if attr == '__call__':
            raise AttributeError("__call__")

        meth = getattr(self, attr)
        return meth(*a, **k)

def providesCallable(class_):
    if hasattr(class_, '__call__'):
        for c in class_.__mro__:
            if '__call__' in c.__dict__:
                return True
    return False
