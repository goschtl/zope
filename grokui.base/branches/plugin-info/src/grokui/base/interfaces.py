# -*- coding: utf-8 -*-

from zope.dublincore.interfaces import IDCDescriptiveProperties
from zope.interface import Interface, Attribute
from zope.schema import TextLine


class IMainMenu(Interface):
    """A menu that allows the access to the different UI panels.
    """


class IUIPanel(Interface):
    """A panel of administration.
    """


class IGrokUIRealm(Interface):
    """Represents an abstract object that acts as the UI namespace.
    It provides an access to the very root folder and to the request.
    """
    root = Attribute("The root folder object.")
    request = Attribute("The HTTP request object.")


class IGrokUIPluginInfo(IDCDescriptiveProperties):
    """Represents a component dedicated to give specific info
    about a grokui extension package.
    """
    version = TextLine(title=u"Version of the package")
