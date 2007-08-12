import zope.interface
import zope.schema
import z3c.schema.email
from z3c.authentication.simple.interfaces import IMember
from z3c.resource.interfaces import IResourceTraversable
from z3c.resource.interfaces import IResourceItem

from tfws.website.i18n import MessageFactory as _


#class IContent(IResourceTraversable): # grok traversal enough for me?
# I need to get a better understanding of IResource.
class IContent(zope.interface.Interface):
    """Page interface."""

    title = zope.schema.TextLine(
        title=_(u'Title'),
        description=_(u'Title of the content.'),
        default=u'',
        required=False)

    description = zope.schema.Text(
        title=_(u'Description'),
        description=_(u'Description of the content.'),
        default=u'',
        required=False)

    keyword = zope.schema.Text(
        title=_(u'Keyword'),
        description=_(u'Keyword of the content.'),
        default=u'',
        required=False)

    body = zope.schema.Text(
        title=_(u'Body'),
        description=_(u'Body is the main part of the page.'),
        default=u'',
        required=False)


class IWebSite(IContent):
    """grok/mars/z3c demo site."""


class IPage(IContent):
    """Page for site."""


class IFolderIndex(zope.interface.Interface):
    """Marker interface for page providing IFolderIndex"""


class IIndexFolder(zope.interface.Interface):
    """Marker interface for adapting to IContent"""


class IWebSiteMember(IMember):
    """WebSite member."""

    lastName = zope.schema.TextLine(
        title=_(u'Last Name'),
        description=_(u'The last name of the administrator.'),
        default=u'',
        missing_value=u'',
        required=True)

    firstName = zope.schema.TextLine(
        title=_(u'First Name'),
        description=_(u'The first name of the administrator.'),
        default=u'',
        missing_value=u'',
        required=True)

    email = z3c.schema.email.field.RFC822MailAddress(
        title=_(u'Email'),
        description=_(u'The email address of the administrator.'),
        required=True)

class IMembers(zope.interface.Interface):
    """Marker interface"""

class IPassword(zope.interface.Interface):

    change_password = zope.schema.Password(
        title=_(u'Change Password'),
        required=False)

    verify_password = zope.schema.Password(
        title=_(u'Verify Password'),
        required=False)

    @zope.interface.invariant
    def areEqual(data):
        if data.change_password != data.verify_password:
            raise zope.interface.Invalid(_("Passwords do not match"))

