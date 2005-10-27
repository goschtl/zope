"""
Utility Interface Definitions
"""
from zope.interface import Interface

class IReadInterface(Interface):

    def mark(object, interface):
        """Add a marker interface to an object
        """

    def erase(object, interface):
        """Remove a marker interface to an object
        """

    def getDirectlyProvided(context):
        """See IIntrospector"""

    def getDirectlyProvidedNames(context):
        """See IIntrospector"""

    def getAvailableInterfaces(context):
        """See IIntrospector"""

    def getAvailableInterfaceNames(context):
        """See IIntrospector"""

    def getProvided(context):
        """Interfaces provided by context"""

    def getDirectlyProvidedNames(context):
        """Names of interfaces provided by context"""

class IWriteInterface(Interface):

    def update(obj, add=[], remove=[]):
        """Update directly provided interfaces for an instance."""

    def mark(obj, interface):
        """ add interface to interfaces an object directly provides"""

    def erase(obj, interface):
        """ remove interfaces from interfaces an object directly provides"""

class IMarkerUtility(IReadInterface, IWriteInterface):
    """This utility exposes part of the IIntrospector interface from Zope3. And provides
       'mark' and 'erase' methods to add and remove marker interfaces
    """
