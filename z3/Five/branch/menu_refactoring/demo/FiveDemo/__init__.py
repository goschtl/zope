import Products

def initialize(context):
    # after everything is configured, we can use adapters
    from classes import MyClass
    from interfaces import INewInterface

    object = MyClass()
    adapted = INewInterface(object)
    print adapted.anotherMethod()
