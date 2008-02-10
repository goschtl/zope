__docformat__ = "reStructuredText"
import zope.interface
from zope.schema import fieldproperty

from z3c.formdemo.addressbook import interfaces

import grok

class Address(grok.Model):
    zope.interface.implements(interfaces.IAddress)

    street = fieldproperty.FieldProperty(interfaces.IAddress['street'])
    city = fieldproperty.FieldProperty(interfaces.IAddress['city'])
    state = fieldproperty.FieldProperty(interfaces.IAddress['state'])
    zip = fieldproperty.FieldProperty(interfaces.IAddress['zip'])

    def __init__(self, **data):
        for name, value in data.items():
            setattr(self, name, value)


class EMails(zope.location.Location, list):
    pass

class EMail(grok.Model):
    zope.interface.implements(interfaces.IEMail)

    user = fieldproperty.FieldProperty(interfaces.IEMail['user'])
    host = fieldproperty.FieldProperty(interfaces.IEMail['host'])

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


class Phone(grok.Model):
    zope.interface.implements(interfaces.IPhone)

    countryCode = fieldproperty.FieldProperty(interfaces.IPhone['countryCode'])
    areaCode = fieldproperty.FieldProperty(interfaces.IPhone['areaCode'])
    number = fieldproperty.FieldProperty(interfaces.IPhone['number'])
    extension = fieldproperty.FieldProperty(interfaces.IPhone['extension'])

    def __init__(self, **data):
        for name, value in data.items():
            setattr(self, name, value)


class Contact(grok.Model):
    zope.interface.implements(interfaces.IContact)

    firstName = fieldproperty.FieldProperty(interfaces.IContact['firstName'])
    lastName = fieldproperty.FieldProperty(interfaces.IContact['lastName'])
    birthday = fieldproperty.FieldProperty(interfaces.IContact['birthday'])

    addresses = None
    emails = None
    homePhone = None
    cellPhone = None
    workPhone = None

    def __init__(self, **data):
        # Save all values
        for name, value in data.items():
            setattr(self, name, value)

