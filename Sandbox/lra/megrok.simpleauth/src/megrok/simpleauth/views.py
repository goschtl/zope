import grok

from urllib import urlencode

from zope.interface import Interface, implements
from zope.component import getUtility, getUtilitiesFor
from zope.app.authentication import PluggableAuthentication
from zope.app.authentication.interfaces import IPasswordManager
from zope.app.authentication.principalfolder import PrincipalFolder
from zope.app.authentication.principalfolder import InternalPrincipal
from zope.app.authentication.principalfolder import IInternalPrincipal
from zope.app.authentication.session import SessionCredentialsPlugin
from zope.app.container.interfaces import DuplicateIDError
from zope.app.security.interfaces import IAuthentication
from zope.app.security.interfaces import IUnauthenticatedPrincipal
from zope.app.form.browser import RadioWidget, TextWidget
from zope.security.management import checkPermission
from zope.app.securitypolicy.interfaces import IPrincipalPermissionManager
from zope.schema import getFieldNamesInOrder, ValidationError
from zope.schema.interfaces import IField, IIterableSource
from zope.i18n import MessageFactory

_ = MessageFactory('megrok.simpleauth')

class ViewMemberListing(grok.Permission):
    ''' Permission to see the member listing '''
    grok.name('plainlogindemo.ViewMemberListing')

class Master(grok.View):
    """
    The master page template macro.
    
    The template master.pt is used as page macro in most views. Since this
    template uses the logged_in method and message attributes below, it's best
    to make all other views in this app subclasses of Master.
    """
    grok.context(Interface)  # register this view for all objects

    message = '' # used to give feedback

    def logged_in(self):
        # this is the canonical way to tell whether the user is authenticated
        # in Zope 3: check if the principal provides IUnauthenticatedPrincipal
        return not IUnauthenticatedPrincipal.providedBy(self.request.principal)
    
class Index(Master):
    """
    The main page, showing user data and member count.
    """

    def member_count(self):
        # get the authentication utility
        pau = getUtility(IAuthentication)
        return len(pau['principals'])

    
class Login(Master):
    """
    Login form and handler.
    """
    def update(self, login_submit=None):
        if login_submit is not None: # we are handling the login submission
            if self.logged_in(): # if the login was accepted then...
                # redirect to where the user came from, or to the main page
                dest = self.request.get('camefrom', self.application_url())
                self.redirect(dest)
            else: # if the user is still not logged in...
                # then an incorrect login or password was provided
                self.message = _(u'Invalid login name and/or password')

class Logout(grok.View):
    """
    Logout handler.
    """
    grok.context(Interface)
    def render(self):
        # get the session plugin and tell it to logout
        session = getUtility(IAuthentication)['session']
        session.logout(self.request)
        # redirect to the main page
        self.redirect(self.application_url())
        
class FullNameWidget(TextWidget):
    """
    Simple customization: change field label from 'Title' to 'Full Name',
    which makes more sense for a user record.
    """

    label = _(u'Full Name')

class PasswordManagerChoices(RadioWidget):
    """
    Widget to select the passwordManager in charge of hashing or encrypting
    the user's password before storing it.
    """

    label = _(u'Password protection')

    def __init__(self, field, request):
        # the IInternalPrincipal.passwordManagerName field comes with a
        # vocabulary which provides the available utilities providing
        # IPasswordManager; here we just pass that vocabulary to the widget
        super(PasswordManagerChoices, self).__init__(
            field, field.vocabulary, request)
        
class Join(grok.AddForm, Master):
    """
    User registration form.
    """

    form_fields = grok.AutoFields(IInternalPrincipal)
    # use our customized widgets
    form_fields['title'].custom_widget = FullNameWidget
    form_fields['passwordManagerName'].custom_widget = PasswordManagerChoices

    label = _(u'User registration')
    template = grok.PageTemplateFile('form.pt')
    
    @grok.action('Save')
    def save(self, **data):
        '''
        Create an InternalPrincipal with the user data.
        
        This method also grants the ViewMemberListing permission to the user.
        '''
        login = data['login']
        pau = getUtility(IAuthentication)
        principals = pau['principals']
        # create an instance of InternalPrincipal
        principal = InternalPrincipal(**data)
        try:
            principals[login] = principal
        except DuplicateIDError:
            # create a validation exception and assign it to the login field
            msg = _(u'Login name taken. Please choose a different one.') 
            self.widgets['login']._error = ValidationError(msg)
            self.form_reset = False # preserve the values in the fields
        else:
            # grant the user permission to view the member listing
            permission_mngr = IPrincipalPermissionManager(grok.getSite())
            permission_mngr.grantPermissionToPrincipal(
               'plainlogindemo.ViewMemberListing', principals.prefix + login)
            self.redirect(self.url('login')+'?'+urlencode({'login':login}))
                    
class Account(grok.View):
    
    def render(self):
        return 'Not implemented'
    
class Listing(Master):
    '''
    Member listing view.
    
    This demonstrates how to require a permission to view, and also how to
    obtain a list of annotated principals.
    '''

    grok.require('plainlogindemo.ViewMemberListing')

    def field_names(self):        
        return getFieldNamesInOrder(IInternalPrincipal)

    def members(self):
        pau = getUtility(IAuthentication)
        principals = pau['principals']
        roster = []
        for id in sorted(principals.keys()):
            user = principals[id]
            fields = {}
            for field in self.field_names():
                fields[field] = getattr(user, field)
            roster.append(fields)
        return roster
    
    def delete_allowed(self):
        # XXX: this is not the right way to do it... it's just a test
        return self.request.principal.id.endswith('.manager')

    