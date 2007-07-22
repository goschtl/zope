import zope.interface
import zope.schema
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.app.container.interfaces import IContainer
from zope.app.container.constraints import containers
from zope.app.container.constraints import contains
from zope.app.component.interfaces import IPossibleSite
from zope.app.file.interfaces import IFile as ZIFile
from zope.app.file.interfaces import IImage as ZIImage
from zope.app.session.interfaces import ISession
import z3c.schema.email
import z3c.pagelet.interfaces
import z3c.form.interfaces
from z3c.authentication.simple.interfaces import IMember
from z3c.resource.interfaces import IResourceTraversable
from z3c.resource.interfaces import IResourceItem

from tfws.website.i18n import MessageFactory as _


#class IContent(IResourceTraversable): # grok traversal enough for me?
class IContent(zope.interface.Interface):
    """Page interface."""

    title = zope.schema.TextLine(
        title=_(u'Title'),
        description=_(u'Title of the html page.'),
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
    """grok/mars demo site."""

    containers('zope.app.folder.interfaces.IFolder')
    contains('tfws.website.interfaces.IPage')

    title = zope.schema.TextLine(
        title=_(u'Title'),
        description=_(u'The title of the site.'),
        default=u"Grok/Mars/Z3C Demo Site",
        required=True)


class IPage(IContainer, IContent):
    """Page interface."""

    containers('tfws.website.interfaces.IWebSite', 
               'tfws.website.interfaces.IPage')
    contains('tfws.website.interfaces.IPage')


class ISamples(IPage):
    """Container for samples"""

    containers(IWebSite)
    contains('z3c.website.interfaces.ISample')

    title = zope.schema.TextLine(
        title=_("Title"),
        description=_("The application title."),
        required=True)


class ISample(IContent):
    """Base class for Z3C sample objects."""

    containers(ISamples)

    headline = zope.schema.TextLine(
        title=_(u'Headline'),
        description=_(u'The headline for the sample.'),
        default=u'',
        required=False)

    summary = zope.schema.Text(
        title=_(u'Summary'),
        description=_(u'The sumary for the sample.'),
        default=u'',
        required=False)

    author = zope.schema.TextLine(
        title=_(u'Author'),
        description=_(u'The author of the sample.'),
        default=u'',
        required=False)


class ISamplePagelet(z3c.pagelet.interfaces.IPagelet):
    """Sample pagelet using a special IPageletRenderer which includes intro and 
    footer templates."""


class ISampleAddForm(z3c.form.interfaces.IAddForm, 
    z3c.pagelet.interfaces.IPagelet):
    """Sample pagelet using a special IPageletRenderer whic includes intro and 
    footer templates."""


class ISessionData(zope.interface.Interface):
    """Simple data object which offers a field called content."""

    content = zope.schema.Text(
        title=u'Content',
        description=u'The content field',
        default=u'')


class IDemoSession(ISession):
    """Simply session which knows how to set and get a object."""

    def setObject(key, obj):
        """Add a object to the session."""

    def getObject(key, default=None):
        """Get a object from the session."""


class IFile(IResourceItem, ZIFile):
    """File resource item."""


class IImage(IResourceItem, ZIImage):
    """Image resource item."""


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

