import pkg_resources

import grok
from zope.app.folder.interfaces import IRootFolder
from zope.app.security.interfaces import IUnauthenticatedPrincipal

class QuickStart(grok.View):
    grok.context(IRootFolder)
    grok.name('index.html')

    def grok_version(self):
        try:
            version=pkg_resources.require('grok')[0].version
        except:
            version='undefined'
        return version

    def logged_in(self):
        return not IUnauthenticatedPrincipal.providedBy(self.request.principal)

    def apps_available(self):
        apps=[]
        for item in list(self.context.values()):
            apps.append({'name':item.__name__,'url':self.url(item)})
        return apps

    def admin_available(self):
        try:
            admin=bool(pkg_resources.require('grokui.admin')[0])
        except pkg_resources.DistributionNotFound:
            admin=False
        return admin
