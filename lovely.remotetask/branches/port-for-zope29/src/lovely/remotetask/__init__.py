# Make a package.
from lovely.remotetask.service import TaskService, getAutostartServiceNames
from lovely.remotetask.interfaces import ITaskService
from zope.component import getUtilitiesFor
from zope.app.component.hooks import getSite
from Products.Five.site.interfaces import IFiveUtilityRegistry
from Products.CMFCore.interfaces._content import ISiteRoot

def initialize(context):
    # dirty trick, but it works
    app = context._ProductContext__app
    services = getAutostartServiceNames()

    for service in services:
        site_name, service_name = service.split('@')
        if site_name:
            site = getattr(app, site_name, None)
            if site:
                registry = IFiveUtilityRegistry(site)
                utility = registry.getUtility(ITaskService, name=service_name)
                utility.startProcessing()
