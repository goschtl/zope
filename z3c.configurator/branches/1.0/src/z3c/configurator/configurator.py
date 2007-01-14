##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Configurator Implementation

$Id$
"""
__docformat__ = "reStructuredText"
import sys
import zope.component
import zope.interface
import zope.schema

from z3c.configurator import interfaces

# Stati values
NEW = 1
OPEN = 2
CLOSED = 3

def configure(component, data):

    plugins = dict(zope.component.getAdapters(
        (component,), interfaces.IConfigurationPlugin))

    # status is a dict plugin names as keys and stati as values.
    status = dict([(name, NEW) for name in plugins])

    def visit(name):
        """The recursive part of the topological sort

        Raises a CyclicDependencyError if cyclic depencencies are found.
        """
        if status[name] == NEW:
            status[name] = OPEN
            plugin = plugins[name]
            for dep in getattr(plugin, 'dependencies', ()):
                visit(dep)
            plugin(data)
            status[name] = CLOSED

        elif status[name] == CLOSED:
            return

        # Stumbling over an OPEN node means there is a cyclic dependency
        elif status[name] == OPEN:
            raise interfaces.CyclicDependencyError(
                "cyclic dependency at '%s'" % name)


    for name in plugins:
        visit(name)


class ConfigurationPluginBase(object):
    zope.interface.implements(interfaces.IConfigurationPlugin)

    def __init__(self, context):
        self.context = context

    def __call__(self, data):
        raise NotImplemented

class SchemaConfigurationPluginBase(object):
    zope.interface.implements(interfaces.IConfigurationPlugin)
    schema = zope.interface.Interface

    def __init__(self, context):
        self.context = context

    def verify(self, data):
        for name, field in zope.schema.getFields(self.schema).items():
            field.validate(data[name])

    def __call__(self, data):
        raise NotImplemented
