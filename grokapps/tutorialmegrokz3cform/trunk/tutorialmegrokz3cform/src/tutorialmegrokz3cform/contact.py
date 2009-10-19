import grok
import persistent
import zope.interface
from zope.schema import fieldproperty
from examplemegrokz3cform import interfaces

class Contact(grok.Model):
    grok.implements(interfaces.IContact)

    name = fieldproperty.FieldProperty(interfaces.IContact['name'])
    description = fieldproperty.FieldProperty(interfaces.IContact['description'])

    def __init__(self, name, description):
        self.name = name
        self.description = description
