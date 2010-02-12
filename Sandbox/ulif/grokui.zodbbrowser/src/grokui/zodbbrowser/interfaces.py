"""grokui.zodbbrowser interfaces.
"""
from zope.interface import Interface

class IObjectInfo(Interface):
    """Infos about an ZODB object.
    """
    def getOID():
        """Get the OID of an object.
        """

    def getName():
        """Get the name of an object or None.
        """
        
    def getParent():
        """Get parent of associated object or None.
        """

    def getChildren():
        """Get a list of children objects.
        """
