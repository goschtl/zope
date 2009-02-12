##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
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
"""
$Id$
"""
__docformat__ = "reStructuredText"

import os

import zope.interface
import zope.component.zcml
import zope.configuration.fields
import zope.security.zcml
from zope.configuration.exceptions import ConfigurationError
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.app.component.back35 import LayerField
from zope.app.publisher.browser import viewmeta
from zope.app.component.metadirectives import IBasicViewInformation

import z3c.template.interfaces
from z3c.pagelet.interfaces import IPagelet
from z3c.pagelet.browser import BrowserPagelet
from z3c.pagelet.zcml import pageletDirective, IPageletDirective

from z3c.mvc.template import TemplateFactory
from z3c.mvc.interfaces import IModelTemplate

class IControllerDirective(IPageletDirective):

    permission = zope.security.zcml.Permission(
        title=u"Permission",
        description=u"The permission needed to use the pagelet.",
        required=False,
        )

    view = zope.configuration.fields.Path(
        title=u'Layout template.',
        description=u"Refers to a file containing a page template (should "
                     "end in extension ``.pt`` or ``.html``).",
        required=False,
        )

# Arbitrary keys and values are allowed to be passed to the pagelet.
IControllerDirective.setTaggedValue('keyword_arguments', True)

def controllerDirective(
    _context, class_, name, permission="zope.Public", for_=zope.interface.Interface,
    layer=IDefaultBrowserLayer, view=None, **kwargs):

    globalObject = zope.configuration.fields.GlobalObject().bind(_context)
    for key, value in kwargs.items():
        kwargs[key] = globalObject.fromUnicode(value)

    if view is not None:
        viewDirective(_context, view, controller=class_, layer=layer)




    provides=IPagelet
    allowed_interface=None
    allowed_attributes=None

    # Security map dictionary
    required = {}

    # Get the permission; mainly to correctly handle CheckerPublic.
    permission = viewmeta._handle_permission(_context, permission)

    # The class must be specified.
    if not class_:
        raise ConfigurationError("Must specify a class.")

    if not zope.interface.interfaces.IInterface.providedBy(provides):
        raise ConfigurationError("Provides interface provide IInterface.")

    ifaces = list(zope.interface.Declaration(provides).flattened())
    if IPagelet not in ifaces:
        raise ConfigurationError("Provides interface must inherit IPagelet.")

    # Build a new class that we can use different permission settings if we
    # use the class more then once.
    cdict = {}
    cdict['__name__'] = name
    missing = []
    if class_.__required_kwargs__:
        for kwarg in class_.__required_kwargs__:
            if kwarg not in kwargs.keys():
                missing.append(kwarg)
    if missing:
        raise ConfigurationError("Controller requires the following "
                                 "attributes to be set: %s"%', '.join(missing))
    cdict.update(kwargs)
    new_class = type(class_.__name__, (class_, BrowserPagelet), cdict)

    # Set up permission mapping for various accessible attributes
    viewmeta._handle_allowed_interface(
        _context, allowed_interface, permission, required)
    viewmeta._handle_allowed_attributes(
        _context, allowed_attributes, permission, required)
    viewmeta._handle_allowed_attributes(
        _context, kwargs.keys(), permission, required)
    viewmeta._handle_allowed_attributes(
        _context, ('__call__', 'browserDefault', 'update', 'render',
                   'publishTraverse'), permission, required)

    # Register the interfaces.
    viewmeta._handle_for(_context, for_)

    # provide the custom provides interface if not allready provided
    if not provides.implementedBy(new_class):
        zope.interface.classImplements(new_class, provides)

    # Create the security checker for the new class
    zope.security.checker.defineChecker(new_class,
        zope.security.checker.Checker(required))

    # register pagelet
    _context.action(
        discriminator = ('pagelet', for_, layer, name),
        callable = zope.component.zcml.handler,
        args = ('registerAdapter',
                new_class, (for_, layer), provides, name, _context.info),)


class IViewDirective(zope.interface.Interface):

    view = zope.configuration.fields.Path(
        title=u'Layout template.',
        description=u"Refers to a file containing a page template (should "
                     "end in extension ``.pt`` or ``.html``).",
        required=True,
        )

    controller = zope.configuration.fields.GlobalObject(
        title = u'View',
        description = u'The view for which the template should be available',
        default=zope.interface.Interface,
        required = False,
        )

    layer = zope.configuration.fields.GlobalObject(
        title = u'Layer',
        description = u'The layer for which the template should be available',
        required = False,
        default=IDefaultBrowserLayer,
        )

def viewDirective(
    _context, view, name=u'',
    controller=zope.interface.Interface, layer=IDefaultBrowserLayer,
    provides=IModelTemplate,
    contentType='text/html', macro=None):

    # Make sure that the template exists
    view = os.path.abspath(str(_context.path(view)))
    if not os.path.isfile(view):
        raise ConfigurationError("No such file", view)

    factory = TemplateFactory(view, contentType, macro)
    zope.interface.directlyProvides(factory, provides)

    # register the view
    if name:
        zope.component.zcml.adapter(_context, (factory,), provides,
                                    (controller, layer), name=name)
    else:
        zope.component.zcml.adapter(_context, (factory,), provides,
                                    (controller, layer))
