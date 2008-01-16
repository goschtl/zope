import grok

from urllib import urlencode

from zope.i18n import MessageFactory
from zope.component import getUtility
from zope.app.security.interfaces import IAuthentication
from zope.app.securitypolicy.interfaces import IPrincipalPermissionManager
from zope.schema import getFieldNamesInOrder, ValidationError

from babylogindemo.memberauth import MemberAuthentication
from babylogindemo.members import IMember, Member

_ = MessageFactory('babylogindemo')


class BabyLoginDemo(grok.Application, grok.Container):
    """
    An app that lets users create accounts, login, logout and change their
    passwords.
    """
    grok.local_utility(MemberAuthentication, IAuthentication)
    
    def __init__(self):
        super(BabyLoginDemo,self).__init__()
        self['members'] = grok.Container()


class ViewMemberListing(grok.Permission):
    "Permission to see the member listing"
    grok.name('babylogindemo.ViewMemberListing')


class Master(grok.View):
    """
    The master page template macro.

    The template master.pt is used as page macro in most views. Since this
    template uses the logged_in method and message attributes below, it's best
    to make all other views in this app subclasses of Master.
    """
    grok.context(BabyLoginDemo)

    message = '' # used to give feedback

    def logged_in(self):
        if self.request.principal.id == 'babylogindemo.ac':
            return False
        return True


class Index(Master):
    """
    The main page, showing user data and member count.
    """

    def members(self):
        members = grok.getSite()['members']
        member_count = len(members)
        if member_count == 0:
            return _(u'No one has')
        elif member_count == 1:
            return _(u'One member has')
        else:
            return unicode(member_count) + _(u' members have')

class Login(Master):
    """
    Login form and handler.
    """
    def update(self, login_submit=None):
        if login_submit is not None:
            if self.logged_in():
                dest = self.request.get('camefrom', self.application_url())
                self.redirect(dest)
            else:
                self.message = _(u'Invalid login name and/or password')


class Listing(Master):
    """
    Member listing view.
    
    This demonstrates how to require a permission to view, and also how to
    obtain a list of annotated principals.
    """

    grok.require('babylogindemo.ViewMemberListing')

    def field_names(self):        
        return getFieldNamesInOrder(IMember)

    def members(self):
        members = self.context['members']
        roster = []
        for id in sorted(members.keys()):
            member = members[id]
            fields = {}
            for field in self.field_names():
                fields[field] = getattr(member, field)
            roster.append(fields)
        return roster
    


class Join(grok.AddForm, Master):
    """
    User registration form
    """
    form_fields = grok.AutoFields(IMember)
    label = _(u'Member registration')
    template = grok.PageTemplateFile('form.pt')

    @grok.action('Save')
    def save(self, **data):
        """
        Create a Member and grant it the ViewMemberListing permission.
        """
        login = data['login']
        members = self.context['members']
        member = Member(**data)
        try:
            # if we can already fetch a member object based on the requested
            # login id, then we create a validation exception and assign it
            # to the login field
            members[login]
            msg = _(u'Login name taken. Please choose a different one.') 
            self.widgets['login']._error = ValidationError(msg)
            self.form_reset = False
        except KeyError:
            # login id is not taken so we save the member object
            # and grant the ViewMemberListing permission to the login id
            members[login] = member
            permission_mngr = IPrincipalPermissionManager(grok.getSite())
            permission_mngr.grantPermissionToPrincipal(
               'babylogindemo.ViewMemberListing', 'babylogindemo' + login)
            self.redirect(
                self.url('login') + '?' + urlencode({'login':login})
            )
