##############################################################################
#
# Copyright (c) 2004 Five Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Browser directives

Directives to emulate the 'http://namespaces.zope.org/browser'
namespace in ZCML known from zope.app.

$Id$
"""
import os

from zope.interface import Interface
from zope.component import getGlobalService, ComponentLookupError
from zope.configuration.exceptions import ConfigurationError
from zope.component.servicenames import Presentation
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.publisher.browser.viewmeta import pages as zope_app_pages
from zope.app.component.metaconfigure import handler
from zope.app.component.interface import provideInterface

from viewable import Viewable
from api import BrowserView
from metaclass import makeClass
from security import getSecurityInfo, protectClass, initializeClass
from ComputedAttribute import ComputedAttribute

def page(_context, name, permission, for_,
         layer='default', template=None, class_=None,
         attribute='__call__', menu=None, title=None,
         allowed_interface=None, allowed_attributes=None,
         ):

    try:
        s = getGlobalService(Presentation)
    except ComponentLookupError, err:
        pass

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

    if class_:
        if attribute != '__call__':
            if not hasattr(class_, attribute):
                raise ConfigurationError(
                    "The provided class doesn't have the specified attribute "
                    )
        cdict = getSecurityInfo(class_)
        if template:
            new_class = makeClassForTemplate(template, bases=(class_, ),
                                             cdict=cdict)
        elif attribute != "__call__":
            # we're supposed to make a page for an attribute (read:
            # method) and it's not __call__.  We thus need to create a
            # new class using our mixin for attributes.
            cdict.update({'__page_attribute__': attribute})
            new_class = makeClass(class_.__name__,
                                  (class_, ViewMixinForAttributes),
                                  cdict)

            # in case the attribute does not provide a docstring,
            # ZPublisher refuses to publish it.  So, as a workaround,
            # we provide a stub docstring
            func = getattr(new_class, attribute)
            if not func.__doc__:
                # cannot test for MethodType/UnboundMethod here
                # because of ExtensionClass
                if hasattr(func, 'im_func'):
                    # you can only set a docstring on functions, not
                    # on method objects
                    func = func.im_func
                func.__doc__ = "Stub docstring to make ZPublisher work"
        else:
            # we could use the class verbatim here, but we'll execute
            # some security declarations on it so we really shouldn't
            # modify the original.  So, instead we make a new class
            # with just one base class -- the original
            new_class = makeClass(class_.__name__, (class_,), cdict)

    else:
        # template
        new_class = makeClassForTemplate(template)

    _handle_for(_context, for_)

    _context.action(
        discriminator = ('view', for_, name, IBrowserRequest, layer),
        callable = handler,
        args = (Presentation, 'provideAdapter',
                IBrowserRequest, new_class, name, [for_], Interface, layer,
                _context.info),
        )
    _context.action(
        discriminator = ('five:protectClass', new_class),
        callable = protectClass,
        args = (new_class, permission)
        )
    _context.action(
        discriminator = ('five:initialize:class', new_class),
        callable = initializeClass,
        args = (new_class,)
        )

class pages(zope_app_pages):

    def page(self, _context, name, attribute='__call__', template=None,
             menu=None, title=None):
        return page(_context,
                    name=name,
                    attribute=attribute,
                    template=template,
                    menu=menu, title=title,
                    **(self.opts))

def _handle_for(_context, for_):
    if for_ is not None:
        _context.action(
            discriminator = None,
            callable = provideInterface,
            args = ('', for_)
            )

#
# mixin classes / class factories
#

class ViewMixinForAttributes(BrowserView):

    # we have an attribute that we can simply tell ZPublisher to go to
    def __browser_default__(self, request):
        return self, (self.__page_attribute__,)

    # this is technically not needed because ZPublisher finds our
    # attribute through __browser_default__; but we also want to be
    # able to call pages from python modules, PythonScripts or ZPT
    def __call__(self, *args, **kw):
        attr = self.__page_attribute__
        meth = getattr(self, attr)
        return meth(*args, **kw)

class ViewMixinForTemplates(BrowserView):

    def getId(self):
        """Return our __name__ or the template id
        """
        return getattr(self, '__name__', self.index.getId())

    # short cut to get to macros more easily
    def __getitem__(self, name):
        return self.index.macros[name]

    def _macros(self):
        """ """
        return self.index.macros

    macros = ComputedAttribute(_macros)

    # make the template publishable
    def __call__(self, *args, **kw):
        return self.index(self, *args, **kw)

class ClassicPTFile(ViewPageTemplateFile):

    def getId(self):
        """Return the template id.

        In our case, we just return the file basename for
        backward compatibility.
        """
        fname = os.path.basename(self.pt_source_file())
        return os.path.splitext(fname)[0]

    def title_or_id(self):
        """Return the template title or id.

        In our case, we just return the id
        backward compatibility.
        """
        return self.getId()

    def pt_getContext(self, instance, request, **kw):
        ns = super(ClassicPTFile, self).pt_getContext(instance, request, **kw)
        # Alias here for backwards compat with Zope2 apps that
        # haven't converted to using 'context'. We may wrapp 'here' with
        # a proxy that raises a DeprecationWarning on access.
        # We may also do the same for 'views'.
        ns['here'] = instance.context
        ns['test'] = lambda x, y, z: x and y or z
        return ns

def makeClassForTemplate(src, template=None, used_for=None, bases=(), cdict=None):
    # XXX needs to deal with security from the bases?
    if cdict is None:
        cdict = {}
    cdict.update({'index': ClassicPTFile(src, template)})
    bases += (ViewMixinForTemplates,)
    class_ = makeClass("SimpleViewClass from %s" % src, bases, cdict)

    if used_for is not None:
        class_.__used_for__ = used_for

    return class_
