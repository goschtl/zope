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
"""Address Book Views

$Id$
"""
__docformat__ = "reStructuredText"
import persistent
import zope.interface
import zope.location
from zope.app.container import contained
from zope.schema.fieldproperty import FieldProperty

from z3c.formdemo.addressbook import interfaces


class Address(contained.Contained, persistent.Persistent):
    zope.interface.implements(interfaces.IAddress)

    street = FieldProperty(interfaces.IAddress['street'])
    city = FieldProperty(interfaces.IAddress['city'])
    state = FieldProperty(interfaces.IAddress['state'])
    zip = FieldProperty(interfaces.IAddress['zip'])

    def __init__(self, **data):
        for name, value in data.items():
            setattr(self, name, value)


class EMails(zope.location.Location, list):
    pass

class EMail(contained.Contained, persistent.Persistent):
    zope.interface.implements(interfaces.IEMail)

    user = FieldProperty(interfaces.IEMail['user'])
    host = FieldProperty(interfaces.IEMail['host'])

    def __init__(self, **data):
        for name, value in data.items():
            setattr(self, name, value)

    @apply
    def fullAddress():
        def get(self):
            return self.user + u'@' + self.host
        def set(self, value):
            self.user, self.host = value.split('@')
        return property(get, set)


class Phone(contained.Contained, persistent.Persistent):
    zope.interface.implements(interfaces.IPhone)

    countryCode = FieldProperty(interfaces.IPhone['countryCode'])
    areaCode = FieldProperty(interfaces.IPhone['areaCode'])
    number = FieldProperty(interfaces.IPhone['number'])
    extension = FieldProperty(interfaces.IPhone['extension'])

    def __init__(self, **data):
        for name, value in data.items():
            setattr(self, name, value)


class Contact(contained.Contained, persistent.Persistent):
    zope.interface.implements(interfaces.IContact)

    firstName = FieldProperty(interfaces.IContact['firstName'])
    lastName = FieldProperty(interfaces.IContact['lastName'])
    birthday = FieldProperty(interfaces.IContact['birthday'])

    addresses = None
    emails = None
    homePhone = None
    cellPhone = None
    workPhone = None

    def __init__(self, **data):
        # Save all values
        for name, value in data.items():
            setattr(self, name, value)
