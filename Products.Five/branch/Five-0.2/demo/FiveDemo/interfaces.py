from zope.interface import Interface

class IMyInterface(Interface):
    """This is a Zope 3 interface.
    """
    def someMethod():
        """This method does amazing stuff.
        """

class INewInterface(Interface):
    """The interface we adapt to.
    """

    def anotherMethod():
        """This method does more stuff.
        """
