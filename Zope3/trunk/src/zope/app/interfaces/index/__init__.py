#
# This file is necessary to make this directory a package.

from zope.interface import Interface

class IInterfaceIndexer(Interface):
    """I index objects by first adapting them to an interface, then
       retrieving a field on the adapted object.
    """
    
