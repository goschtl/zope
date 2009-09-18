# -*- coding: utf-8 -*-

import grok
from zope.app.folder.interfaces import IRootFolder
from grokui.base.contentproviders import AdministrationHeader, AdministrationFooter
from zope.component import getUtility
from zope.traversing.browser.absoluteurl import absoluteURL
from zope.app.publisher.interfaces.browser import IBrowserMenu
from zope.app.security.interfaces import IUnauthenticatedPrincipal

grok.context(IRootFolder)
grok.templatedir("templates")
grok.viewletmanager(AdministrationHeader)


class AdministrationMenuViewlet(grok.Viewlet):
    grok.order(40)
    grok.name("admin_menu")

    def update(self):
        self.contexturl = absoluteURL(self.context, self.request)
        menu = getUtility(IBrowserMenu, 'grokui_admin_menu')
        self.actions = menu.getMenuItems(self.context, self.request)
    

class AdministrationBanner(grok.Viewlet):
    grok.order(10)
    grok.name('admin_banner')

    
class GrokRelax(grok.Viewlet):
    grok.order(20)
    grok.name('admin_decoration')


class Messages(grok.Viewlet):
    grok.order(40)
    grok.name('admin_messages')


class LoginInformation(grok.Viewlet):
    grok.order(30)
    grok.name('admin_login')

    @property
    def is_authenticated(self):
        """Check, wether we are authenticated.
        """
        return not IUnauthenticatedPrincipal.providedBy(self.request.principal)

    
class AdministrationAuthors(grok.Viewlet):
    grok.order(10)
    grok.name('admin_authors')
    grok.viewletmanager(AdministrationFooter)
