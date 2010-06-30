"""
Join form
$Id$
"""

from zope.interface import Interface, invariant, Invalid
from zope.schema import ASCIILine, Password, Bool
from zope.formlib import form

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFDefault.formlib.form import EditFormBase
from Products.CMFDefault.formlib.schema import EmailLine
from Products.CMFDefault.permissions import ManageUsers

from Products.CMFDefault.utils import Message as _

def passwords_must_match(pw, confirmation):
    pass


class IJoinSchema(Interface):
    """Zope generates password and sends it by e-mail"""
    
    member_id = ASCIILine(
                    title=_(u"Member ID")
                    )
                    
    email = EmailLine(
                    title=_(u"E-mail address")
                    )
    
    password = Password(
                    title=_(u"Password"),
                    min_length=5
                    )
                    
    confirmation = Password(
                    title=_(u"Password (confirm)"),
                    min_length=5
                    )
                    
    send_password = Bool(
                    title=_(u"Mail Password?"),
                    description=_(u"Check this box to have the password mailed."))
                    
    @invariant
    def check_passwords_match(schema):
        """Password and confirmation must match"""
        if schema.password != schema.confirmation:
            raise Invalid(_(u"Passwords do not match"))


class Join(EditFormBase):
    
    base_template = EditFormBase.template
    template = ViewPageTemplateFile("join.pt")
    registered = False
    form_fields = form.FormFields(IJoinSchema)
    
    actions = form.Actions(
        form.Action(
            name='register',
            label=_(u'Register'),
            validator="validate_username",
            success='handle_register_success',
            failure='handle_failure'),
        form.Action(
            name='cancel',
            label=_(u'Cancel')
                )
            )
    
    def __init__(self, context, request):
        super(Join, self).__init__(context, request)
        ptool = self._getTool("portal_properties")
        self.validate_email = ptool.getProperty('validate_email', None)
        if self.validate_email:
            self.form_fields = self.form_fields.select('member_id', 'email')
        self.rtool = self._getTool('portal_registration')
        self.mtool = self._getTool('portal_membership')

    @property
    def isAnon(self):
        return self.mtool.isAnonymousUser()
                
    @property
    def isManager(self):
        return self.mtool.checkPermission(ManageUsers, self.mtool)
        
    @property
    def isOrdinaryMember(self):
        return not (self.registered or self.isManager or self.isAnon)

    @property
    def title(self):
        if self.isManager:
            return _(u"Register a new member")
        else:
            return _(u'Become a Member')
                    
    def setUpWidgets(self, ignore_request=False):
        """If e-mail validation is in effect, users cannot select passwords"""
        super(Join, self).setUpWidgets(ignore_request)

    def personalize(self):
        atool = self._getTool('portal_actions')
        return atool.getActionInfo("user/preferences")['url']
        
    def validate_username(self, action, data):
        """Avoid duplicate registration"""
        errors = super(Join, self).validate(action, data)
        member = self.mtool.getMemberById(data.get('member_id', None))
        if member is not None:
            errors.append(_(u"The login name you selected is already in use or is not valid. Please choose another."))
        return errors

    def add_member(self, data):
        """Add new member and notify if requested or required"""
        self.rtool.addMember(
                        id=data['member_id'],
                        password=data['password'],
                             properties={
                                        'username': data['member_id'],
                                        'email': data['email']
                                        }
                        )
        if self.validate_email or data['send_password']:
            self.rtool.registeredNotify(data['member_id'])
        self.registered = True
        self.label = _(u'Success')
        
    def handle_register_success(self, action, data):
        """Register user and inform they have been registered"""
        if self.validate_email:
            data['password'] = self.rtool.generatePassword()
        self.add_member(data)
        self.status = _(u'You have been registered as a member.')
        if not self.validate_email:
            self._setRedirect('portal_actions', 'user/login')