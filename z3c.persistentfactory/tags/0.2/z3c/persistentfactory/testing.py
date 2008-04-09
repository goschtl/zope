from zope import interface, component

try:
    from zope.component import eventtesting
except ImportError:
    from zope.app.event.tests import placelesssetup as eventtesting

from z3c.persistentfactory import factory

class IFoo(interface.Interface): pass
class IBar(interface.Interface): pass
class IBaz(interface.Interface): pass
class IQux(interface.Interface): pass

class Foo(object): pass

class Bar(object):

    @interface.implementer(IBar)
    @component.adapter(IFoo)
    def factory(self, *args, **kw):
        return self, args, kw

class Baz(object):

    @factory.factory
    @interface.implementer(IBar)
    @component.adapter(IFoo)
    def factory(self, *args, **kw):
        print 'Called %s' % self.factory.__call__
        print '  args: %s' % (args,)
        print '  kwargs: %s' % kw
        return self.factory.__call__, args, kw
