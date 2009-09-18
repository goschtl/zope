# -*- coding: utf-8 -*-

import grok
from megrok.menu import Menu
from zope.app.folder.interfaces import IRootFolder
from grokui.base.interfaces import IApplicationRepresentation
from grokui.base.interfaces import IApplicationInformation


class AdministrationHeader(grok.ViewletManager):
    grok.name('grokui_admin_header')
    grok.context(IRootFolder)


class AdministrationFooter(grok.ViewletManager):
    grok.name('grokui_admin_footer')
    grok.context(IRootFolder)


class ApplicationInformation(grok.ViewletManager):
    grok.name('grokui_application_info')
    grok.context(IApplicationRepresentation)


class AdministrationMenu(Menu):
    grok.context(IRootFolder)
    grok.name('grokui_admin_menu')
    grok.title('Administration panels')
