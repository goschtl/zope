import grok
import persistent
import zope.interface
from zope.schema import fieldproperty
import interfaces

class HelloWorld(grok.Model):
    grok.implements(interfaces.IHelloWorld)

    who = fieldproperty.FieldProperty(interfaces.IHelloWorld['who'])
    when = fieldproperty.FieldProperty(interfaces.IHelloWorld['when'])
    what = fieldproperty.FieldProperty(interfaces.IHelloWorld['what'])

    def __init__(self, who, when, what):
        self.who = who
        self.when = when
        self.what = what

