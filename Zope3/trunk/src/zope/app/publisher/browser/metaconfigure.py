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
from zope.component.interfaces import IDefaultViewName
from zope.configuration.exceptions import ConfigurationError
from zope.interface.interface import InterfaceClass
from zope.publisher.interfaces.browser import ILayer, ISkin, IDefaultSkin
from zope.publisher.interfaces.browser import IBrowserRequest

from zope.app import zapi
from zope.app.component.metaconfigure import handler
from zope.app.container.interfaces import IAdding
from zope.app.publisher.browser.globalbrowsermenuservice \
     import menuItemDirective
from zope.app.component.contentdirective import ContentDirective

# referred to through ZCML
from zope.app.publisher.browser.resourcemeta import resource
from zope.app.publisher.browser.resourcemeta import resourceDirectory
from zope.app.publisher.browser.i18nresourcemeta import I18nResource
from zope.app.publisher.browser.viewmeta import view
from zope.app.component.interface import provideInterface

from zope.app.component.interface import provideInterface

# Create special modules that contain all layers and skins
from types import ModuleType as module
import sys
layers = module('layers')
sys.modules['zope.app.layers'] = layers

skins = module('skins')
sys.modules['zope.app.skins'] = skins


def layer(_context, name=None, interface=None, base=IBrowserRequest):
    """Provides a new layer.

    >>> class Context(object):
    ...     info = u'doc'
    ...     def __init__(self): self.actions = []
    ...     def action(self, **kw): self.actions.append(kw)

    Possibility 1: The Old Way
    --------------------------
    
    >>> context = Context()
    >>> layer(context, u'layer1')
    >>> iface = context.actions[0]['args'][1]
    >>> iface.getName()
    u'layer1'
    >>> iface.__bases__
    (<InterfaceClass zope.publisher.interfaces.browser.IBrowserRequest>,)
    >>> hasattr(sys.modules['zope.app.layers'], 'layer1')
    True

    >>> del sys.modules['zope.app.layers'].layer1

    Possibility 2: Providing a custom base interface
    ------------------------------------------------
    
    >>> class BaseLayer(IBrowserRequest):
    ...     pass
    >>> context = Context()
    >>> layer(context, u'layer1', base=BaseLayer)
    >>> iface = context.actions[0]['args'][1]
    >>> iface.getName()
    u'layer1'
    >>> iface.__bases__
    (<InterfaceClass zope.app.publisher.browser.metaconfigure.BaseLayer>,)
    >>> hasattr(sys.modules['zope.app.layers'], 'layer1')
    True

    >>> del sys.modules['zope.app.layers'].layer1

    Possibility 3: Define a Layer just through an Interface
    -------------------------------------------------------

    >>> class layer1(IBrowserRequest):
    ...     pass
    >>> context = Context()
    >>> layer(context, interface=layer1)
    >>> context.actions[0]['args'][1] is layer1
    True
    >>> hasattr(sys.modules['zope.app.layers'], 'layer1')
    False

    Here are some disallowed configurations.

    >>> context = Context()
    >>> layer(context, 'foo,bar')
    Traceback (most recent call last):
    ...
    TypeError: Commas are not allowed in layer names.
    >>> layer(context)
    Traceback (most recent call last):
    ...
    ConfigurationError: You must specify the 'name' or 'interface' attribute.
    >>> layer(context, base=BaseLayer)
    Traceback (most recent call last):
    ...
    ConfigurationError: You must specify the 'name' or 'interface' attribute.

    >>> layer(context, interface=layer1, base=BaseLayer)
    Traceback (most recent call last):
    ...
    ConfigurationError: You cannot specify the 'interface' and 'base' together.
    """
    if name is not None and ',' in name:
        raise TypeError("Commas are not allowed in layer names.")
    if name is None and interface is None: 
        raise ConfigurationError(
            "You must specify the 'name' or 'interface' attribute.")
    if interface is not None and base is not IBrowserRequest:
        raise ConfigurationError(
            "You cannot specify the 'interface' and 'base' together.")

    if interface is None:
        interface = InterfaceClass(name, (base, ),
                                   __doc__='Layer: %s' %name,
                                   __module__='zope.app.layers')
        # Add the layer to the skins module.
        # Note: We have to do this immediately, so that directives using the
        # InterfaceField can find the layer.
        setattr(layers, name, interface)
        path = 'zope.app.layers.'+name
    else:
        path = name = interface.__module__ + '.' + interface.getName()


    # Register the layer interface as an interface
    _context.action(
        discriminator = ('interface', path),
        callable = provideInterface,
        args = (path, interface),
        kw = {'info': _context.info}
        )

    # Register the layer interface as a layer
    _context.action(
        discriminator = ('layer', name),
        callable = provideInterface,
        args = (name, interface, ILayer, _context.info)
        )

def skin(_context, name=None, interface=None, layers=None):
    """Provides a new layer.

    >>> import pprint
    >>> class Context(object):
    ...     info = u'doc'
    ...     def __init__(self): self.actions = []
    ...     def action(self, **kw): self.actions.append(kw)

    >>> class Layer1(IBrowserRequest): pass
    >>> class Layer2(IBrowserRequest): pass

    Possibility 1: The Old Way
    --------------------------
    
    >>> context = Context()
    >>> skin(context, u'skin1', layers=[Layer1, Layer2])
    >>> iface = context.actions[0]['args'][1]
    >>> iface.getName()
    u'skin1'
    >>> pprint.pprint(iface.__bases__)
    (<InterfaceClass zope.app.publisher.browser.metaconfigure.Layer1>,
     <InterfaceClass zope.app.publisher.browser.metaconfigure.Layer2>)
    >>> hasattr(sys.modules['zope.app.skins'], 'skin1')
    True

    >>> del sys.modules['zope.app.skins'].skin1

    Possibility 2: Just specify an interface
    ----------------------------------------

    >>> class skin1(Layer1, Layer2):
    ...     pass

    >>> context = Context()
    >>> skin(context, interface=skin1)
    >>> context.actions[0]['args'][1] is skin1
    True

    Here are some disallowed configurations.

    >>> context = Context()
    >>> skin(context)
    Traceback (most recent call last):
    ...
    ConfigurationError: You must specify the 'name' or 'interface' attribute.
    >>> skin(context, layers=[Layer1])
    Traceback (most recent call last):
    ...
    ConfigurationError: You must specify the 'name' or 'interface' attribute.

    >>> skin(context, name=u'skin1')
    Traceback (most recent call last):
    ...
    ConfigurationError: You must specify the 'name' and 'layers' attribute.
    """
    if name is None and interface is None: 
        raise ConfigurationError(
            "You must specify the 'name' or 'interface' attribute.")
    if (name is not None and layers is None) or \
       (name is None and layers is not None): 
        raise ConfigurationError(
            "You must specify the 'name' and 'layers' attribute.")

    if name is not None:
        interface = InterfaceClass(name, layers,
                                   __doc__='Skin: %s' %name,
                                   __module__='zope.app.skins')
        # Add the layer to the skins module.
        # Note: We have to do this immediately, so that directives using the
        # InterfaceField can find the layer.
        setattr(skins, name, interface)
        path = 'zope.app.skins'+name
    else:
        path = name = interface.__module__ + '.' + interface.getName()

    # Register the layer interface as an interface
    _context.action(
        discriminator = ('interface', path),
        callable = provideInterface,
        args = (path, interface),
        kw = {'info': _context.info}
        )

    # Register the layer interface as a layer
    _context.action(
        discriminator = ('skin', name),
        callable = provideInterface,
        args = (name, interface, ISkin, _context.info)
        )

def setDefaultSkin(name, info=''):
    """Set the default skin.

    >>> from zope.interface import directlyProvides
    >>> from zope.app.tests import ztapi

    >>> class Skin1(IBrowserRequest): pass
    >>> directlyProvides(Skin1, ISkin)

    >>> ztapi.provideUtility(ISkin, Skin1, 'Skin1')
    >>> setDefaultSkin('Skin1')
    >>> adapters = zapi.getService(zapi.servicenames.Adapters)
    >>> adapters.lookup((IBrowserRequest,), IDefaultSkin, '') is Skin1
    True
    """
    skin = zapi.getUtility(ISkin, name)
    handler('Adapters', 'register',
            (IBrowserRequest,), IDefaultSkin, '', skin, info),

def defaultSkin(_context, name):

    _context.action(
        discriminator = 'defaultSkin',
        callable = setDefaultSkin,
        args = (name, _context.info)
        )

def defaultView(_context, name, for_=None):

    type = IBrowserRequest

    _context.action(
        discriminator = ('defaultViewName', for_, type, name),
        callable = handler,
        args = (zapi.servicenames.Adapters, 'register',
                (for_, type), IDefaultViewName, '', name, _context.info)
        )

    if for_ is not None:
        _context.action(
            discriminator = None,
            callable = provideInterface,
            args = ('', for_)
            )


def addMenuItem(_context, title, class_=None, factory=None, description='',
                permission=None, filter=None, view=None):
    """Create an add menu item for a given class or factory

    As a convenience, a class can be provided, in which case, a
    factory is automatically defined based on the class.  In this
    case, the factory id is based on the class name.

    """
    
    if class_ is None:
        if factory is None:
            raise ValueError("Must specify either class or factory")
    else:
        if factory is not None:
            raise ValueError("Can't specify both class and factory")
        if permission is None:
            raise ValueError(
                "A permission must be specified when a class is used")
        factory = "zope.app.browser.add.%s.%s" % (
            class_.__module__, class_.__name__) 
        ContentDirective(_context, class_).factory(
            _context,
            id = factory)

    extra = {'factory': factory}

    if view:
        action = view
    else:
        action = factory

    menuItemDirective(_context, 'zope.app.container.add', IAdding,
                      action, title, description, filter,
                      permission, extra)
