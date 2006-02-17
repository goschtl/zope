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
"""Configuration handlers for 'dav' namespace.

$Id$
"""
__docformat__ = 'restructuredtext'

from zope import component
from zope.schema import getFieldNamesInOrder
from zope.app.component.metaconfigure import utility
from zope.app.component.metaconfigure import adapter
from zope.app.component.interface import provideInterface
from zope.interface import directlyProvides
from interfaces import IDAVNamespace

from interfaces import INamespaceManager
from namespaces import NamespaceManager

def interface(_context, for_, interface):
    directlyProvides(interface, IDAVNamespace)
    utility(_context, IDAVNamespace, interface, name=for_)
from zope.deprecation import deprecated
deprecated(interface,
           'provideInterface is no more - use namespace, schemas directive')

################################################################################
#
# New WebDAV registration.
#
################################################################################

def _addWidgetToRegistry(registry, propertyname, class_):
    registry.registerWidget(propertyname, class_)


class namespace(object):
    def __init__(self, _context, namespace, schemas = [],
                 restricted_properties = [], interfaceType = None):
        self._context = _context
        self.namespace = namespace
        self.schemas = schemas
        self.restricted_properties = restricted_properties
        self.interfaceType = interfaceType

        self.widgets = {}

    def widget(self, _context, propname, class_):
        self.widgets[propname] = class_

    def __call__(self):
        registry = NamespaceManager(self.namespace, self.schemas,
                                    self.restricted_properties,
                                    self.interfaceType)

        #
        # Create a new INamespaceManager Utility
        #
        utility(self._context, INamespaceManager, registry,
                name = self.namespace)

        #
        # Register all the widgets if they are specified
        #
        for prop, widgetclass in self.widgets.items():
            registry.registerWidget(prop, widgetclass)

        #
        # Declare all schemas to implement the interfaceType if it is not None
        #
        if self.interfaceType is not None:
            interfaceType = self.interfaceType
            path = interfaceType.__module__ + '.' + interfaceType.__name__

            self._context.action(
                discriminator = None,
                callable = provideInterface,
                args = (path, interfaceType),
                )

            for schema in self.schemas:
                self._context.action(
                    discriminator = None,
                    callable = provideInterface,
                    args = ('', schema, interfaceType),
                    )


class schemas(object):
    def __init__(self, _context, namespace, schemas,
                 restricted_properties = ()):
        self._context = _context
        self.namespace = namespace
        self.schemas = schemas
        self.restricted_properties = restricted_properties
        self.widgets = {}

    def widget(self, _context, propname, class_):
        self.widgets[propname] = class_

    def callaction(self):
        registry = component.getUtility(INamespaceManager, self.namespace)
        #
        # Register all the schemas
        #
        for schema in self.schemas:
            registry.registerSchema(schema, self.restricted_properties)

        #
        # Register all the widgets
        #
        for prop, widgetclass in self.widgets.items():
            registry.registerWidget(prop, widgetclass)

        #
        # Declare all interface to implement interfaceType since we want
        # these interfaces to show up in the APIDOC tool.
        #
        if registry.interfaceType is not None:
            for schema in self.schemas:
                provideInterface('', schema, registry.interfaceType)

    def __call__(self):
        #
        # Need to make self.schemas hashable for the discriminator to work
        # correctly - this could be done a lot nicer I am guesing.
        #
        discriminator = ('dav:schemas', self.namespace)
        for schema in self.schemas:
            discriminator += ('%s.%s' %(schema.__module__, schema.__name__),)
        self._context.action(
            discriminator = discriminator,
            callable = self.callaction,
            args = (),
            )


def widgetHandler(namespace, propname, class_):
    registry = component.getUtility(INamespaceManager, namespace)
    registry.registerWidget(propname, class_)


def widget(_context, namespace, propname, class_):
    #
    # We can't just ask for the namespace here since it is unlikely to
    # have being created yet.
    #
    _context.action(
        discriminator = ('dav.namepsacewidget', namespace, propname),
        callable = widgetHandler,
        args = (namespace, propname, class_),
        )
