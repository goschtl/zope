# -*- coding: utf-8 -*-

import grok
import megrok.menu
from megrok.layout import Layout, Page
from grokui.base.namespace import GrokUILayer
from grokui.base.interfaces import IAdminPanel
from zope.app.folder.interfaces import IRootFolder
from zope.traversing.browser.absoluteurl import absoluteURL


grok.layer(GrokUILayer)
grok.templatedir("templates")


class AdminLayout(Layout):
    """The general layout for the administration
    """
    grok.context(IRootFolder)
    title = u"Grok Administration Interface"


class AdminView(Page):
    """An admin view.
    """
    grok.baseclass()
    grok.context(IRootFolder)
    grok.implements(IAdminPanel)
    megrok.menu.menuitem('grokui_admin_menu')
    
