import Products

def initialize(context):
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
