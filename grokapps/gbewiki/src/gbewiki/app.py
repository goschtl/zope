import grok
from zope.app.authentication import PluggableAuthentication
from zope.app.authentication.principalfolder import PrincipalFolder
from zope.app.authentication.session import SessionCredentialsPlugin
from zope.app.security.interfaces import IAuthentication

from gbewiki.page import Page, default_page_name
from gbewiki.utils import WikiWords, AutoLink, ListOfPages, ITransform

def setup_pau_principal(pau):
    """Callback to setup the Pluggable Authentication Utility """
    pau['principals'] = PrincipalFolder() 
    pau.authenticatorPlugins = ('principals',)
    pau['session'] = session = SessionCredentialsPlugin()
    session.loginpagename = 'login'
    pau.credentialsPlugins = ('No Challenge if Authenticated', 'session',)

class PermissionEditPage(grok.Permission):
    """Permission to edit a Page """
    grok.name('wiki.EditPage')
    
class PermissionAddPage(grok.Permission):
    """Permission to add a Page """
    grok.name('wiki.AddPage')
  
class WikiPage(grok.Application, grok.Container):
    grok.local_utility(PluggableAuthentication, IAuthentication,
                       setup=setup_pau_principal)
    
    def traverse(self, page_name=default_page_name):
        """default page name is MainPage
        create a new page object if page_name does not exist already """
        page=self.get(page_name)
        if page is None:
            page=Page(page_name)
        return page

class WikiPageIndex(grok.View):
    """default application view """
    grok.name('index')
    
    def render(self):
        self.redirect('%s/%s' % (self.application_url(),default_page_name))
        return
                
class Add(grok.View):
    grok.require('wiki.AddPage')
    
    def render(self):
        name=self.request['name']
        page=Page(name)
        page.content=self.request['content']
        page.editor=self.request.principal.title
        self.context[name]=page
        grok.notify(grok.ObjectCreatedEvent(page))
        self.flash('Page was added')
        self.redirect(self.url(page))
     
