# -*- coding: utf-8 -*-

import grok
import megrok.menu
import z3c.flashmessage.interfaces

from grok import util
from grokui.base import IGrokUIRealm, GrokUILayer, IUIPanel, MainMenu
from megrok.layout import Layout, Page
from zope.component import getUtility
from zope.traversing.browser.absoluteurl import absoluteURL

grok.layer(GrokUILayer)
grok.templatedir("templates")


class GrokUILayout(Layout):
    """The general layout for the administration
    """
    grok.context(IGrokUIRealm)
    title = u"Grok User Interface"

    def update(self):
        self.baseurl = absoluteURL(self.context, self.request) + '/'
        

class GrokUIView(Page):
    """A grok ui view.
    """
    grok.baseclass()
    grok.context(IGrokUIRealm)
    grok.implements(IUIPanel)
    megrok.menu.menuitem(MainMenu)

    def application_url(self, name=None, data=None):
        return util.application_url(self.request, self.context, name, data)

    def flash(self, message, type='message'):
        source = getUtility(
            z3c.flashmessage.interfaces.IMessageSource, name='session')
        source.send(message, type)
