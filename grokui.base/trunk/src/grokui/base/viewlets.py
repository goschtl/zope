# -*- coding: utf-8 -*-

import grok
from zope.component import getUtility
from zope.app.folder.interfaces import IRootFolder
from zope.app.publisher.interfaces.browser import IBrowserMenu
from zope.app.security.interfaces import IUnauthenticatedPrincipal
from z3c.flashmessage.interfaces import IMessageReceiver
from grokui.base import IGrokuiRealm
from grokui.base.interfaces import IAdminPanel
from grokui.base.contentproviders import AdministrationHeader
from grokui.base.contentproviders import AdministrationFooter

grok.templatedir("templates")

grok.view(IAdminPanel)
grok.context(IGrokuiRealm)
grok.viewletmanager(AdministrationHeader)


class Banner(grok.Viewlet):
    grok.order(10)
    grok.name('grokui.banner')


class LoginInformation(grok.Viewlet):
    grok.order(20)
    grok.name('grokui.login')

    @property
    def is_authenticated(self):
        """Check, wether we are authenticated.
        """
        return not IUnauthenticatedPrincipal.providedBy(self.request.principal)


class MenuViewlet(grok.Viewlet):
    grok.order(30)
    grok.name("grokui.menu")

    def update(self):
        menu = getUtility(IBrowserMenu, 'grokui_admin_menu')
        self.rooturl = self.view.url(self.context)
        self.actions = menu.getMenuItems(self.context, self.request)


class Messages(grok.Viewlet):
    grok.order(40)
    grok.name('grokui.messages')

    @property
    def messages(self):
        receiver = getUtility(IMessageReceiver)
        return receiver.receive()


class Authors(grok.Viewlet):
    grok.order(10)
    grok.name('grokui.authors')
    grok.viewletmanager(AdministrationFooter)
