# -*- coding: utf-8 -*-

import megrok.menu
import grokcore.view as grok
from megrok.layout import Layout, Page
from grokui.base import IGrokUIRealm, GrokUILayer, IUIPanel, MainMenu


grok.layer(GrokUILayer)
grok.templatedir("templates")


class GrokUILayout(Layout):
    """The general layout for the administration
    """
    grok.context(IGrokUIRealm)
    title = u"Grok User Interface"


class GrokUIView(Page):
    """A grok ui view.
    """
    grok.baseclass()
    grok.context(IGrokUIRealm)
    grok.implements(IUIPanel)
    megrok.menu.menuitem(MainMenu)
