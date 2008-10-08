import persistent
import zope.interface
from zope.location import location
from zope.schema import fieldproperty
from talk.z3cform import interfaces

class HelloWorldMessage(location.Location, persistent.Persistent):
    zope.interface.implements(interfaces.IHelloWorldMessage)

    who = fieldproperty.FieldProperty(interfaces.IHelloWorldMessage['who'])
    when = fieldproperty.FieldProperty(interfaces.IHelloWorldMessage['when'])
    what = fieldproperty.FieldProperty(interfaces.IHelloWorldMessage['what'])

    def __init__(self, who, when, what):
        self.who = who
        self.when = when
        self.what = what
