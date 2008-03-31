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
""" `browser:cssregistry` directive

$Id$
"""

from zope import schema, interface
from zope.component.zcml import handler
from zope.configuration.fields import GlobalObject

from i18n import _
from property import CSSProperty
from registry import CSSRegistry, registries

from interfaces import ICSSRegistry, ICSSRegistryLayer


class ICSSRegistryDirective(interface.Interface):

    name = schema.TextLine(
	title = _(u'Name'),
        description = _(u'Registry name'),
	required = False)

    title = schema.TextLine(
	title = _(u'Title'),
	required = False)

    layer = GlobalObject(
        title=_(u"The layer the css registry should be found in"),
        required=False)


class ICSSPropertySubDirective(interface.Interface):

    name = schema.TextLine(
	title = _(u'Name'),
        description = _(u'Property name'),
	required = True)

    value = schema.TextLine(
	title = _(u'Value'),
        description = _(u'Property value'),
	required = True)

    description = schema.TextLine(
	title = _(u'Description'),
        description = _(u'Property description'),
	required = False)

    type = schema.TextLine(
	title = _(u'Type'),
        description = _(u'Property type. (color, font, size)'),
	required = False)
    

class ICSSPropertyDirective(interface.Interface):

    registry = schema.TextLine(
	title = _(u'Registry'),
	required = False)

    layer = GlobalObject(
        title = _(u"The layer the css registry should be found in"),
        required=False)

    name = schema.TextLine(
	title = _(u'Name'),
	required = True)

    value = schema.TextLine(
	title = _(u'Value'),
	required = True)

    description = schema.TextLine(
	title = _(u'Description'),
        description = _(u'Property description'),
	required = False)

    type = schema.TextLine(
	title = _(u'Type'),
        description = _(u'Property type. (color, font, size)'),
	required = False)


class Factory(object):
    
    def __init__(self, registry):
        self.registry = registry

    def __call__(self, layer1, layer2, request):
        return self.registry


class cssregistryHandler(object):

    def __init__(self, _context, name='', title='', layer=interface.Interface):
        self.name = name
        self.layer = layer

        self.registry = CSSRegistry()
        self.registry.name = name
        self.registry.title = title

        registries[(name, layer)] = self.registry

        # we can't use just 'layer', because registry will be registered as resource 
        _context.action(
	    discriminator = ('CSSRegistry', name, layer),
	    callable = handler,
	    args = ('registerAdapter',
		    Factory(self.registry),
		    (ICSSRegistryLayer, ICSSRegistryLayer, layer),
                    ICSSRegistry, name, _context.info),
	    )

    def property(self, _context, name, value, description='', type=''):
        self.registry[name] = CSSProperty(name, value, description, type)


def csspropertyHandler(_context, name, value, registry='', 
                       layer=interface.Interface, description='', type=''):
    registry = registries[(registry, layer)]
    registry[name] = CSSProperty(name, value, description, type)
