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
""" z3ext.skintool interfaces

$Id$
"""
from zope import schema, interface
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('z3ext')


class ISkinable(interface.Interface):
    """ marker interface for skinable objects """


class IDefaultLayer(interface.interfaces.IInterface):
    """ default layer (automaticlly added to skin) """


class IDefaultLayers(interface.Interface):
    """ adapter that provide default layers """

    layers = interface.Attribute('tuple of ILayer interfaces')


class ISkinTool(interface.Interface):
    """ skin tool, allow generate skin on the fly """

    user_layers = schema.List(
        title = _(u'Layers'),
        description = _(u'Select skin layers.'),
        value_type = schema.Choice(vocabulary = "z3ext skin layers"),
        default = [],
        required = False)

    def generate():
        """ generate skin interface """
