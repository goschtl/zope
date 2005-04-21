from zope.interface import implements, Interface
from interfaces import IAdaptable, IAdapted, IOrigin, IDestination

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

class Adaptable:
    implements(IAdaptable)

    def method(self):
        return "The method"

class Adapter:
    implements(IAdapted)

    def __init__(self, context):
        self.context = context

    def adaptedMethod(self):
        return "Adapted: %s" % self.context.method()

class Origin:
    implements(IOrigin)

class OriginalAdapter:
    implements(IDestination)

    def __init__(self, context):
        self.context = context

    def method(self):
        return "Original"

class OverrideAdapter:
    implements(IDestination)

    def __init__(self, context):
        self.context = context

    def method(self):
        return "Overridden"
