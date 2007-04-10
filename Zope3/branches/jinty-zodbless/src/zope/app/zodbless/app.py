from zope.interface import implements, Interface
from zope.component import getGlobalSiteManager
from zope.location import Location
from zope.traversing.interfaces import IContainmentRoot
from zope.app.component.interfaces import ISite
from zope.app.appsetup.interfaces import IApplicationFactory

class IMyApplication(Interface):
    """Marker interface to hang views onto."""
    pass

class Application(Location):
    """A simple application."""

    # If you want resources to work, ISite must come before IContainmentRoot
    implements(IMyApplication, ISite, IContainmentRoot)

    def setSiteManager(self, sm):
        # no ZODB to set the site manager in, but we want resources, so...
        raise NotImplementedError()

    def getSiteManager(self):
        return getGlobalSiteManager()

class ApplicationFactory:
    implements(IApplicationFactory)

    def prepare(self):
        pass

    def __call__(self, request):
        return Application()

app_factory = ApplicationFactory()
