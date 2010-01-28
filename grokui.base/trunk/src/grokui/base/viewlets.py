# -*- coding: utf-8 -*-

import grok
from grokui.base import Header, Footer, IUIPanel, IGrokUIRealm
from z3c.flashmessage.interfaces import IMessageReceiver
from zope.browsermenu.interfaces import IBrowserMenu
from zope.authentication.interfaces import IUnauthenticatedPrincipal
from zope.component import getUtility


grok.view(IUIPanel)
grok.context(IGrokUIRealm)
grok.templatedir("templates")
grok.viewletmanager(Header)


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
        menu = getUtility(IBrowserMenu, "grokui_mainmenu")
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
    grok.viewletmanager(Footer)
