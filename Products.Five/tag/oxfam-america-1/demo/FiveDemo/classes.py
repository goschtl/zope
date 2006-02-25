from zope.interface import implements
from interfaces import IMyInterface, INewInterface

class MyClass:
    implements(IMyInterface)

    def someMethod(self):
        return "I am alive! Alive!"

class MyAdapter:
    implements(INewInterface)

    def __init__(self, context):
        self.context = context

    def anotherMethod(self):
        return "We have adapted: %s" % self.context.someMethod()
