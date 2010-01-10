# -*- coding: utf-8 -*-

import grok
from megrok.menu import Menu
from grokui.base import IGrokuiRealm
from grokui.base.interfaces import IApplicationRepresentation
from grokui.base.interfaces import IApplicationInformation


class AdministrationHeader(grok.ViewletManager):
    grok.name('grokui_admin_header')
    grok.context(IGrokuiRealm)


class AdministrationFooter(grok.ViewletManager):
    grok.name('grokui_admin_footer')
    grok.context(IGrokuiRealm)


class ApplicationInformation(grok.ViewletManager):
    grok.name('grokui_application_info')
    grok.context(IApplicationRepresentation)


class AdministrationMenu(Menu):
    grok.context(IGrokuiRealm)
    grok.name('grokui_admin_menu')
    grok.title('Administration panels')
