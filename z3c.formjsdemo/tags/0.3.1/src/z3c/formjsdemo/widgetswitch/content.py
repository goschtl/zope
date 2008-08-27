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
"""Widget Switch Content

$Id$
"""
__docformat__="restructuredtext"
import zope.interface
from zope.schema.fieldproperty import FieldProperty
from z3c.formjsdemo.widgetswitch import interfaces

class Contact(object):
    zope.interface.implements(interfaces.IContact)

    name = FieldProperty(interfaces.IContact['name'])
    street = FieldProperty(interfaces.IContact['street'])
    city = FieldProperty(interfaces.IContact['city'])
    zip = FieldProperty(interfaces.IContact['zip'])
    phone = FieldProperty(interfaces.IContact['phone'])
    age = FieldProperty(interfaces.IContact['age'])
