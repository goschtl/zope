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

def requiredPlugins(component, names=[]):

    """returns a list of tuples (name, plugin) in the right order to
    be executed"""
    
    plugins = dict(zope.component.getAdapters(
        (component,), interfaces.IConfigurationPlugin))
    # if we have no names we return them all
    if not names:
        return [(name, plugins[name]) for name in sorted(plugins.keys())]
    
    def _add(name, res):
        deps = getattr(plugins[name], 'dependencies', ())
        for dep in deps:
            if not dep in res:
                _add(dep, res)
        if name not in res:
            res.append(name)
    res = []
    for name in names:
        _add(name, res)
    return [(name, plugins[name]) for name in res]

def configure(component, data, names=[], useNameSpaces=False):

    plugins = requiredPlugins(component, names)
    for name, plugin in plugins:
        if useNameSpaces is True:
            d = data.get(name, {})
        else:
            d = data
            
        plugin(d)

class ConfigurationPluginBase(object):
    zope.interface.implements(interfaces.IConfigurationPlugin)

    def __init__(self, context):
        self.context = context

    def __call__(self, data):
        raise NotImplemented

class SchemaConfigurationPluginBase(object):
    zope.interface.implements(interfaces.ISchemaConfigurationPlugin)
    schema = zope.interface.Interface

    def __init__(self, context):
        self.context = context

    def verify(self, data):
        for name, field in zope.schema.getFields(self.schema).items():
            field.validate(data[name])

    def __call__(self, data):
        raise NotImplemented
