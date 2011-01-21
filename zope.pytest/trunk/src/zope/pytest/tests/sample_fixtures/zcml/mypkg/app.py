import zope.interface

class AppSample(object):
    pass

class IFoo(zope.interface.Interface):
    def do_foo():
        pass

class FooUtility(object):
    zope.interface.implements(IFoo)

    def do_foo(self):
        return "Foo!"
