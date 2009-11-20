# -*- coding: utf-8 -*-

from zope.interface import Interface, Attribute
from grokcore.view.components import DirectoryResource


class ILibrary(Interface):
    """A library, including resources.
    """
    name = Attribute("The name of the library needed for URL computations")
    

class Library(DirectoryResource):
    """A library that can include resources.
    """
    name = None
