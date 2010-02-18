# -*- coding: utf-8 -*-

from zope.interface import Interface, Attribute


class IResourcesIncluder(Interface):
    """A publishable component that can include resources.
    """


class ILibrary(Interface):
    """A library, including resources.
    """
    name = Attribute("The name of the library needed for URL computations")
