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

from zope import schema,interface
from z3c.reference import interfaces
import types


class ViewReferenceField(schema.Object):
    interface.implements(interfaces.IViewReferenceField)

    def __init__(self, **kw):
        settingName = kw.pop('settingName', u'')
        self.settingName = settingName
        super(ViewReferenceField,self).__init__(interfaces.IViewReference,
                                                **kw)


class ImageReferenceField(schema.Object):
    interface.implements(interfaces.IImageReferenceField)
    size = schema.fieldproperty.FieldProperty(
        interfaces.IImageReferenceField['size'])
    
    def __init__(self,**kw):
        self.size = kw.pop('size',None)
        super(ImageReferenceField,self).__init__(interfaces.IImageReference,
                                                 **kw)


class ObjectReferenceField(ViewReferenceField):
    interface.implements(interfaces.IObjectReferenceField)

    def __init__(self,refSchema,**kw):
        self.refSchema = refSchema
        super(ObjectReferenceField,self).__init__(**kw)

