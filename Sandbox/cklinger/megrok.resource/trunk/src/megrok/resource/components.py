# -*- coding: utf-8 -*-

from grokcore.component import baseclass
from grokcore.view import View
from zope.interface import Interface, Attribute, classImplements


class IResourcesIncluder(Interface):
    """A publishable component that can include resources.
    """

classImplements(View, IResourcesIncluder)


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
