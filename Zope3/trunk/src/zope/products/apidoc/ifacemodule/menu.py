##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Interface Module Browser Menu (Tree)

A list of interfaces from the Interface Service is pretty much unmanagable and
is very confusing. Therefore it is nice to split the path of the interface, so
that we get a deeper tree with nodes having shorter, manageable names.

$Id: menu.py,v 1.1 2004/01/29 17:51:16 srichter Exp $
"""
from zope.app import zapi
from zope.interface import implements
from zope.app.interfaces.location import ILocation
from zope.app.location import LocationProxy
from zope.products.statictree.interfaces import IChildObjects
from zope.products.apidoc.ifacemodule import IInterfaceModule
from zope.products.apidoc.utilities import ReadContainerBase
from zope.proxy import removeAllProxies

class IModule(ILocation):
    """Represents some module

    Marker interface, so that we can register an adapter for it."""
    

class Module(ReadContainerBase):
    r"""Represents a Python module

    Examples: zope, zope.app, zope.app.interfaces

    However, we usually use it only for the last case.

    Usage::

      >>> from zope.products.apidoc.ifacemodule import tests
      >>> from zope.products.apidoc.ifacemodule import InterfaceModule
      >>> tests.setUp()

      >>> module = Module(InterfaceModule(), 'zope.products')
      >>> module.get('apidoc.interfaces.IDocumentationModule').getName()
      'IDocumentationModule'

      >>> module.get(
      ...     'zope.products.apidoc.interfaces.IDocumentationModule') is None
      True

      >>> print '\n'.join([id for id, iface in module.items()])
      zope.products.apidoc.interfaces.IDocumentationModule

      >>> tests.tearDown()
    """
    
    implements(IModule)

    def __init__(self, parent, name):
        self.__parent__ = parent
        self.__name__ = name

    def get(self, key, default=None):
        name = self.__name__ + '.' + key
        return self.__parent__.get(name, default)

    def items(self):
        parent = self.__parent__
        items = []
        for key in parent.keys():
            if key.startswith(self.__name__):
                items.append((key, LocationProxy(parent[key], self, key)))
        return items


class InterfaceModuleChildObjects:
    r"""Module Adapter for Static Tree

    This adapter is used when building a static tree for the browser.

    Functionality::

      >>> from zope.products.apidoc.ifacemodule import tests
      >>> from zope.products.apidoc.ifacemodule import InterfaceModule
      >>> tests.setUp()

      >>> module = InterfaceModule()
      >>> module = tests.rootLocation(module, 'Interface')
      >>> adapter = InterfaceModuleChildObjects(module)
      >>> adapter.hasChildren()
      True

      >>> print '\n'.join([c.__name__ for c in adapter.getChildObjects()])
      IInterfaceModule
      zope.products.apidoc.interfaces

      >>> tests.tearDown()      
    """

    implements(IChildObjects)
    __used_for__ = IInterfaceModule

    def __init__(self, context):
        self.context = context

    def hasChildren(self):
        """See zope.products.statictree.interfaces.IChildObject"""
        return bool(len(self.context))

    def getChildObjects(self):
        """See zope.products.statictree.interfaces.IChildObject"""
        objects = {}
        names = removeAllProxies(self.context.keys())
        names.sort()
        for name in names:
            # Split these long names and make part of the module path separate
            # entries. Currently we only split by the term '.interfaces', but
            # a more sophisticated algorithm could be developed. 
            iface_loc = name.find('.interfaces')
            if iface_loc == -1:
                objects[name] = LocationProxy(self.context[name],
                                              self.context, name)
            else:
                module_name = name[:iface_loc+11]
                objects[module_name] = Module(self.context, module_name)
        items = objects.items()
        items.sort()
        return [x[1] for x in items]


class Menu(object):
    """Menu View Helper Class

    A class that helps building the menu. The menu_macros expects the menu view
    class to have the getMenuTitle(node) and getMenuLink(node) methods
    implemented. 'node' is a 'zope.products.statictree.node.Node' instance.
    """

    def getMenuTitle(self, node):
        """Return the title of the node that is displayed in the menu."""
        if isinstance(removeAllProxies(node.context.__parent__), Module):
            parent = node.context.__parent__
            return zapi.name(node.context).replace(zapi.name(parent)+'.', '')
        return zapi.name(node.context)

    def getMenuLink(self, node):
        """Return the HTML link of the node that is displayed in the menu."""
        if isinstance(removeAllProxies(node.context), Module):
            return None

        return './' + zapi.name(node.context) + '/apiindex.html'
