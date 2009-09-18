import grok
from zope.interface import Interface
from zope.component import getUtility
from zope.traversing.browser.absoluteurl import absoluteURL
from zope.app.publisher.interfaces.browser import IBrowserMenu
from rdbz3cformexample.app import RDBExampleIndex, RDBExample

grok.templatedir("templates")
grok.context(RDBExample)

class LinksViewletManager(grok.ViewletManager):
    grok.name("rdb_links")

class LinksViewlet(grok.Viewlet):
    grok.view(RDBExampleIndex)
    
    def update(self):
        self.contexturl = absoluteURL(self.context, self.request)
        menu = getUtility(IBrowserMenu, 'rdb_links_menu')
        self.actions = menu.getMenuItems(self.context, self.request)


