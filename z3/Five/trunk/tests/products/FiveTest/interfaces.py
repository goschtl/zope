from zope.interface import Interface

class IAdaptable(Interface):
    """This is a Zope 3 interface.
    """
    def method(self):
        """This method will be adapted
        """

class IAdapted(Interface):
    """The interface we adapt to.
    """

    def adaptedMethod(self):
        """A method to adapt.
        """

class ISimpleContent(Interface):
    pass
