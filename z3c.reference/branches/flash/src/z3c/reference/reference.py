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

import zope.interface
import zope.component
from zope.dublincore.property import DCProperty
from zope.schema.fieldproperty import FieldProperty
from zope.annotation.interfaces import IAttributeAnnotatable
from lovely.relation.property import (FieldRelationManager,
                                      RelationPropertyOut)
from z3c.reference import interfaces


viewReferenceRelated = FieldRelationManager(
    interfaces.IViewReference['target'], 
    interfaces.IReferenced['viewReferences'])


class ViewReference(persistent.Persistent):

    zope.interface.implements(interfaces.IViewReference, IAttributeAnnotatable)

    view = FieldProperty(interfaces.IViewReference['view'])
    target = RelationPropertyOut(viewReferenceRelated)

    title = DCProperty('title')
    description = DCProperty('description')
    
    def __init__(self,target=None,view=None):
        if target is not None:
            self.target = target
        if view is not None:
            self.view = view

    def __eq__(self,other):
        if not other:
            return False
        if interfaces.IViewReference.providedBy(other):
            return (self.view == other.view) and \
                   (self.target is other.target)
        return False

    def __ne__(self,other):
        if not other:
            return True
        if interfaces.IViewReference.providedBy(other):
            return (self.view != other.view) or \
                   (self.target != other.target)
        return True


class ImageReference(ViewReference):
    zope.interface.implements(interfaces.IImageReference)


class DefaultViewReferenceSettings(object):
    """Default view reference settings adapter."""

    zope.interface.implements(interfaces.IViewReferenceSettings)

    def __init__(self, context):
        self.context = context

    @property
    def settings(self):
        return {}

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.context.__name__)

