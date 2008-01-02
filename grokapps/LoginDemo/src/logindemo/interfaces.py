import re

from zope.interface import Interface, implements
from zope import schema
from zope.component import adapts, getUtilitiesFor
from zope.annotation.interfaces import IAnnotations
from zope.app.authentication.principalfolder import IInternalPrincipal
from zope.app.authentication.interfaces import IPasswordManager
from persistent.dict import PersistentDict
from zope.i18n import MessageFactory

_ = MessageFactory('logindemo')

USER_DATA_KEY = 'logindemo.iuser.data' 

class NotAnEmailAddress(schema.ValidationError):
    __doc__ = _(u"Invalid email address")

check_email = re.compile(r"[a-zA-Z0-9._%-]+@([a-zA-Z0-9-]+\.)*[a-zA-Z]{2,4}").match
def validate_email(value):
    if check_email(value):
        return True
    raise NotAnEmailAddress(value)

class PasswordManagerChoices(object):
    implements(schema.interfaces.IIterableSource)
    
    def __init__(self):
        self.choices = [name for name, util in
                            sorted(getUtilitiesFor(IPasswordManager))]
        
    def __iter__(self):
        return iter(self.choices)
    
    def __len__(self):
        return len(self.choices)
    
    def __contains__(self, value):
        return value in self.choices

class IUser(Interface):
    """Basic user data."""
    login = schema.TextLine(title=_(u"Login"),
                            required=True)
    password = schema.Password(title=_(u"Password"),
                            required=True)
    # XXX: I have not managed yet to display this in the app.py join form
    #password_encoding = schema.Choice(title=_(u"Password encoding"),
    #                        required=True,
    #                        source=PasswordManagerChoices())
    name = schema.TextLine(title=_(u"Full name"),
                            required=False)
    email = schema.ASCIILine(title=_(u"E-mail"),
                            required=False,
                            constraint=validate_email)

class UserDataAdapter(object): 
    """
    Principal Information Adapter
    
    Fields which are common to both IUser and IInternalPrincipal are stored
    in the context, an InternalPrincipal instance.
    
    The IUser.name field is stored in the title attr of the InternalPrincipal.
    
    Remaining fields of IUser (such as email) are stored as annotations on the
    InternalPrincipal instance.
    """ 
    implements(IUser)
    adapts(IInternalPrincipal)

    def __init__(self , context):
        annotations = IAnnotations(context)
        self.context = context
        self.data = annotations.get(USER_DATA_KEY)
        if self.data is None:
            self.data = PersistentDict()
            for field in IUser:
                if field not in IInternalPrincipal:
                    self.data[field] = u''
            annotations[USER_DATA_KEY] = self.data
        
    def __getattr__(self, name):
        if name in IUser:
            if name == 'name':
                return self.context.title
            elif name in IInternalPrincipal:
                return getattr(self.context, name)
            return self.data.get(name)
        else:
            raise AttributeError, '%s not in IUser'
        
    def __setattr__(self, name, value):
        if name in ['context','data']:
            super(UserDataAdapter,self).__setattr__(name , value)
        elif name in IUser:
            if name in IInternalPrincipal:
                setattr(self.context, name, value)
            elif name == 'name':
                setattr(self.context, 'title', value)
            else:
                self.data[name] = value
        else:
            raise AttributeError, '%s not in IUser'
