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

from interfaces import *
from persistent import Persistent
from zope.schema.fieldproperty import FieldProperty
from zope.cachedescriptors.property import readproperty
from zope.dublincore.interfaces import IZopeDublinCore
from zope.app.keyreference.interfaces import IKeyReference
from zope import interface
from zope.traversing.browser.absoluteurl import absoluteURL
import urlparse,cgi
from lovely.relation.property import (FieldRelationManager,
                                      RelationPropertyOut)


viewReferenceRelated = FieldRelationManager(IViewReference['target'],
                                            IReferenced['viewReferences'])


class ViewReference(Persistent):
    interface.implements(IViewReference)

    view = FieldProperty(IViewReference['view'])
    target = RelationPropertyOut(viewReferenceRelated)
    
    def __init__(self,target=None,view=None):
        if target is not None:
            self.target = target
        self.view = view

    def __eq__(self,other):
        if not other:
            return False
        if IViewReference.providedBy(other):
            return (self.view == other.view) and \
                   (self.target is other.target)
        return False

    def __ne__(self,other):
        if not other:
            return True
        if IViewReference.providedBy(other):
            return (self.view != other.view) or \
                   (self.target != other.target)
        return True
        

class ImageReference(ViewReference):
    interface.implements(IImageReference)
    
