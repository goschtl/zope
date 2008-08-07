##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
""" z3ext:layer directive

$Id$
"""
from zope import schema, interface, component
from zope.configuration.fields import Tokens, GlobalInterface, PythonIdentifier

from z3ext.skintool.tool import layers_byname, layers_registry


class ILayerDirective(interface.Interface):

    layer = GlobalInterface(
	title = u'Layer',
        description = u'Skin layer.',
	required = True)

    name = PythonIdentifier(
	title = u'Name',
	description = u'Content name.',
	required = True)

    title = schema.TextLine(
	title = u'Title',
	description = u'Content title.',
	required = True)

    description = schema.TextLine(
	title = u'Description',
	description = u'Content description.',
	required = False)

    require = Tokens(
        title = u'Require',
        description = u'Interface of other layers that are '\
            u'required by this layer.',
        required = False,
        value_type = GlobalInterface())


def layerDirectiveHandler(_context, layer, name, title,
                          description='', require=[]):
    _context.action(
	discriminator = ('z3ext.skintool-layer', layer, name),
	callable = layerDirective,
	args = (layer, name, title, description, require))


def layerDirective(layer, name, title, description, require):
    sitemanager = component.getGlobalSiteManager()

    layers_byname[name] = layer
    layers_registry[layer] = (layer, name, title, description, require)
