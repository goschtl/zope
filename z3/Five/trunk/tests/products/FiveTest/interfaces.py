from zope.interface import Interface

class IAdaptable(Interface):
    """This is a Zope 3 interface.
    """
    def method():
        """This method will be adapted
        """

class IAdapted(Interface):
    """The interface we adapt to.
    """

    def adaptedMethod():
        """A method to adapt.
        """

class IOrigin(Interface):
    """Something we'll adapt"""

class IDestination(Interface):
    """The result of an adaption"""

    def method():
	"""Do something"""

class ISimpleContent(Interface):
    pass

class ICallableSimpleContent(ISimpleContent):
    pass

class IIndexSimpleContent(ISimpleContent):
    pass

class IFancyContent(Interface):
    pass
