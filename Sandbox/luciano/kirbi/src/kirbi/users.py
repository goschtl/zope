import grok
from zope.app.authentication.principalfolder import PrincipalFolder, PrincipalInfo, InternalPrincipal
from zope.app.authentication.interfaces import IPrincipalInfo


class UserFolder(grok.Container, PrincipalFolder):
    pass

class User(InternalPrincipal):
    pass

class Index(grok.View):
    grok.context(UserFolder)
    def update(self, query=None):
        self.results_title = '%d users' % len(self.context)

    
class Register(grok.AddForm):
    grok.context(UserFolder)
    """ User registration form """
    
    form_fields = grok.AutoFields(IPrincipalInfo)

    @grok.action('Add entry')
    def add(self, **data):
        self.context[id] = User(**data)
        self.redirect(self.url('users'))

