# -*- coding: utf-8 -*-

from zope import schema
from zope.location import ILocation
from zope.interface import Interface
from zope.contentprovider.interfaces import IContentProvider


class IAdminPanelMenu(Interface):
    """A menu that allows the access to the different administration panels.
    """


class IAdminPanel(Interface):
    """A panel of administration.
    """


class IApplication(Interface):
    """Defines an Grok application 
    """
    classname = schema.ASCIILine(
        title = u"Dotted name of the Application class",
        required = True
        )
    
    description = schema.Text(
        title = u"Description of the Application",
        default = u"",
        required = False
        )


class IInstallableApplication(IApplication):
    """Defines an installable application.
    """


class IInstalledApplication(IApplication, ILocation):
    """Defines an application that is installed in our system.
    """
    url = schema.URI(
        title = u"Absolute URL of the application",
        required = True
        )


class IApplicationInformation(IContentProvider):
    """Marker interface for the Application information content provider.
    """
