from zope import interface, component

from z3c.persistentfactory import declarations, factory

class IFoo(interface.Interface): pass
class IBar(interface.Interface): pass
class IBaz(interface.Interface): pass
class IQux(interface.Interface): pass

class Foo(object): pass

class Bar(object):

    @interface.implementer(IBar)
    @component.adapter(IFoo)
    def factory(self):
        return self

class Baz(object):

    @factory.factory
    @interface.implementer(IBar)
    @component.adapter(IFoo)
    def factory(self):
        return self
