import re

import grok
from zope.interface import Interface
from zope.component import getUtility
from zope.dublincore.interfaces import IZopeDublinCore
from zope.app.authentication.principalfolder import InternalPrincipal
from zope.app.security.interfaces import IAuthentication
from zope.app.security.interfaces import IUnauthenticatedPrincipal
from zope.app.securitypolicy.interfaces import IPrincipalPermissionManager
import z3c.flashmessage.interfaces

grok.context(Interface)

class WikiMaster(grok.View):
    """The master page template macro """

    def logged_in(self):
        return not IUnauthenticatedPrincipal.providedBy(self.request.principal)
    
    def user(self):
        if not self.logged_in():
            return None
        else:
            return self.request.principal.title

    def isManager(self):
        return self.request.principal.id == 'zope.manager'
    
    def exists(self,name=''):
        if not(name):
            if self.context.__class__.__name__ == 'Page':
                parent=self.context.__parent__
                name=self.context.__name__
            else:
                parent=self.context
        else:
            parent=self.context.__parent__
        return name in parent.keys()
    
    def isWikiName(self, name=''):
        regexp = re.compile(r'[A-Z][a-z]+([A-Z][a-z]+)+')
        return list(regexp.finditer(name))
    
    def dc(self):
        return IZopeDublinCore(self.context)
    
    def editor(self):
        if self.context.__class__.__name__ == 'Page':
            if self.exists():
                return self.context.editor
        return None
    
    def messages(self):
        source = getUtility(
            z3c.flashmessage.interfaces.IMessageSource, name='session')
        for message in list(source.list('message')):
            message.prepare(source)
            yield message

    def js_tiny(self):
        out="""
tinyMCE.init({
mode: "textareas",
theme: "advanced",
content_css: "%s",
auto_focus: "mce_editor_0"
});
""" % self.static['style.css']()
        return out
   
    def js_newpage(self):
        out="""
function NewPage() {
  var pageName = window.prompt("Enter the WikiName of your new page:");
  if (pageName) {
    location.href = '%s/' + pageName;
  }
}
""" % self.application_url()
        return out
    
class Login(WikiMaster):
    """Login form and handler."""
    def update(self, login_submit=None):
        if login_submit is not None:
            if self.logged_in(): 
                dest = self.request.get('camefrom', self.application_url())
                self.flash('Welcome back, %s. You are now logged in' % \
                           self.request.principal.id)
                self.redirect(dest)
            else:
                # create a new principal from the request data
                if not (self.request.get('login') in self.members()):
                    login=self.request.get('login')
                    password=self.request.get('password')
                    pau = getUtility(IAuthentication)
                    principals = pau['principals']
                    principal = InternalPrincipal(login, password, login,
                                  passwordManagerName='SHA1')
                    principals[login] = principal
                    permission_mngr = IPrincipalPermissionManager(grok.getSite())
                    permission_mngr.grantPermissionToPrincipal(
                       'wiki.AddPage', principals.prefix + login)
                    permission_mngr.grantPermissionToPrincipal(
                       'wiki.EditPage', principals.prefix + login)
                    dest = self.request.get('camefrom', self.application_url())
                    self.flash('Your account has been created. You are now \
                    logged in')
                    self.redirect(dest)

    def members(self):
        pau = getUtility(IAuthentication)
        principals = pau['principals']
        return list(sorted(principals.keys()))

class Logout(grok.View):
    """Logout handler."""
    def render(self):
        session = getUtility(IAuthentication)['session']
        session.logout(self.request)
        self.flash('You are now logged out')
        self.redirect(self.application_url())
        