# -*- coding: utf-8 -*-

from grokcore.component import baseclass
from zope.interface import Interface, Attribute


class IResourcesIncluder(Interface):
    """A publishable component that can include resources.
    """


class ILibrary(Interface):
    """A library, including resources.
    """
    name = Attribute("The name of the library needed for URL computations")

    
class Library(object):
    """A library that exposes resources through an URL.
    This component is only used to declare a resources folder.
    """
    baseclass()
    name = None
