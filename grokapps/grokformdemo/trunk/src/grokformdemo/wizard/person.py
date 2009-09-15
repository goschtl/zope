import grok
import zope.schema 
import zope.interface

from z3c.wizard import wizard, step
from megrok.z3cform import wizard as z3cwizard
from zope.location.interfaces import ILocation
from zope.schema.fieldproperty import FieldProperty



class IPerson(ILocation):
    """Person interface."""

    firstName = zope.schema.TextLine(title=u'First Name')
    lastName = zope.schema.TextLine(title=u'Last Name')
    street = zope.schema.TextLine(title=u'Street')
    city = zope.schema.TextLine(title=u'City')


class Person(grok.Model):
    """Person content."""
    grok.implements(IPerson)

    firstName = FieldProperty(IPerson['firstName'])
    lastName = FieldProperty(IPerson['lastName'])
    street = FieldProperty(IPerson['street'])
    city = FieldProperty(IPerson['city'])

