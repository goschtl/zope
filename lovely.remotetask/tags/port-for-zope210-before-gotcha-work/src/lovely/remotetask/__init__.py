# Make a package.
from lovely.remotetask.service import TaskService

try:
    from Products.Five.site.interfaces import IFiveUtilityRegistry
    ZOPE2=True
except ImportError:
    ZOPE2=False
    
# This is implemented as IDatabaseOpenedEvent in Zope 3
if ZOPE2:
    from lovely.remotetask.service import TaskService, getAutostartServiceNames
    from lovely.remotetask.interfaces import ITaskService
    from zope.component import ComponentLookupError
    from zope.app.component.hooks import getSite, setSite
    from Products.CMFCore.interfaces._content import ISiteRoot

    def initialize(context):
        # dirty trick, but it works
        app = context._ProductContext__app
        services = getAutostartServiceNames()
        old_site = getSite()
        for service in services:
            site_name, service_name = service.split('@')
            if site_name:
                site = getattr(app, site_name, None)
                if site:
                    registry = site.getSiteManager()
                    setSite(site)  # blah, five/localsitemanager/registry.py ver. 1.1, line 108, in _wrap can't find site.
                    service = registry.getUtility(ITaskService, name=service_name)
                    if ITaskService.providedBy(service) and not service.isProcessing():
                        service.startProcessing()
        setSite(old_site)
