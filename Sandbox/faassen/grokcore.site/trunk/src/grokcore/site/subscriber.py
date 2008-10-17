import grokcore.component
from zope.app.component.site import LocalSiteManager
from zope.app.container.interfaces import IObjectAddedEvent

from grokcore.site.components import Site

@grokcore.component.subscribe(Site, IObjectAddedEvent)
def addSiteHandler(site, event):
    sitemanager = LocalSiteManager(site)
    # LocalSiteManager creates the 'default' folder in its __init__.
    # It's not needed anymore in new versions of Zope 3, therefore we
    # remove it
    del sitemanager['default']
    site.setSiteManager(sitemanager)
