##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
__docformat__ = 'restructuredtext'

import persistent

from zope import interface
from zope import component

from zope.annotation.factory import factory
from zope.schema.fieldproperty import FieldProperty

from z3c.reference import interfaces

from lovely.relation.interfaces import IDataRelationship


class ViewReference(persistent.Persistent):
    interface.implements(interfaces.IViewReference)
    component.adapts(IDataRelationship)

    view = FieldProperty(interfaces.IViewReference['view'])

viewReferenceFactory = factory(ViewReference)


class DefaultViewReferenceSettings(object):
    """Default view reference settings adapter."""
    interface.implements(interfaces.IViewReferenceSettings)

    def __init__(self, context):
        self.context = context

    settings = {}

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.context.__name__)

