import grok
import megrok.menu
from megrok.layout import Layout, Page
from zope.app.folder.interfaces import IRootFolder

grok.templatedir("templates")


class AdminLayout(Layout):
    """The general layout for the administration
    """
    grok.context(IRootFolder)
    template = grok.PageTemplateFile('templates/adminlayout.pt')
    title = u"Grok Administration Interface"
    

class AdminView(Page):
    """An admin view.
    """
    grok.baseclass()
    grok.context(IRootFolder)
    megrok.menu.menuitem('grokui_admin_menu')
