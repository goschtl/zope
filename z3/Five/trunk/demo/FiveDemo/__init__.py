from Products.Five import zcml
import Products

def initialize(context):
    zcml.process('configure.zcml', package=Products.FiveDemo)

    # after everything is configured, we can use adapters
    
    from zope.component import getAdapter
    from classes import MyClass
    from interfaces import INewInterface
    
    object = MyClass()
    adapted = getAdapter(object, INewInterface)
    print adapted.anotherMethod()

    # shortcut
    adapted = INewInterface(object)
    print adapted.anotherMethod()
