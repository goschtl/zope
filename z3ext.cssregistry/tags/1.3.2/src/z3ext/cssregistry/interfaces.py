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
""" z3ext.cssregistry interfaces

$Id$
"""
from zope import schema, interface
from zope.interface.common.mapping import IMapping
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('z3ext.cssregistry')


class ICSSRegistry(IMapping):

    properties = interface.Attribute('css properties')

    name = schema.TextLine(
	title = _(u'Name'),
	description = _(u'CSS Registry name'),
	default = u'',
	required = False)

    title = schema.TextLine(
	title = _(u'Title'),
	description = _(u'CSS Registry title'),
	default = u'',
	required = False)


class ICSSProperty(interface.Interface):

    name = schema.TextLine(
	title = _(u'Name'),
	description = _(u'Property name'),
	required = True)

    title = schema.TextLine(
	title = _(u'Title'),
        description = _(u'Property title'),
	required = False)

    description = schema.TextLine(
	title = _(u'Description'),
        description = _(u'Property description'),
	required = False)

    value = schema.TextLine(
	title = _(u'Value'),
	description = _(u'Property value'),
	required = True)

    type = schema.TextLine(
	title = _(u'Type'),
        description = _(u'Property type. (color, font, size)'),
	required = False)

    def process(text):
        """ replace property in text """
    

class ICSSRegistryLayer(interface.Interface):
    """ marker interface """


class Layer(object):
    interface.implements(ICSSRegistryLayer)

Layer = Layer()


class ICSSRegistryConfiglet(ICSSRegistry):
    """ css registry configlet """

    enabled = schema.Bool(
        title = _(u'Enabled'),
        default = False,
        required = True)
