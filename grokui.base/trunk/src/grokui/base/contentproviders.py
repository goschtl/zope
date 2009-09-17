import grok
from megrok.menu import Menu
from grokui.base.interfaces import IApplication
from grokui.base.interfaces import IApplicationInformation


class AdministrationMenu(Menu):
    grok.name('grokui_admin_menu')
    grok.title('Administration panels')


class ApplicationInformation(grok.ViewletManager):
    grok.context(IApplication)
    
