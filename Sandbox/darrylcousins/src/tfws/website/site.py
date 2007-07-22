import zope.component
import zope.interface
import zope.schema
import zope.event
import zope.lifecycleevent
from zope.schema.fieldproperty import FieldProperty
from zope.traversing.browser import absoluteURL
from zope.app.intid import IntIds
from zope.app.intid.interfaces import IIntIds
from zope.app.catalog.catalog import Catalog
from zope.app.catalog.interfaces import ICatalog
from zope.app.folder.interfaces import IRootFolder
from zope.app.authentication.session import SessionCredentialsPlugin
from zope.app.security.interfaces import IAuthentication
from zope.app.securitypolicy.interfaces import IPrincipalRoleManager

from z3c.authentication.simple.authentication import SimpleAuthentication
from z3c.authentication.simple.group import Group
from z3c.authentication.simple.group import GroupContainer
from z3c.authentication.simple.member import Member
from z3c.authentication.simple.member import MemberContainer
from z3c.authentication.simple.interfaces import IAuthenticatedPrincipal
from z3c.authentication.simple.interfaces import IFoundPrincipal
from z3c.authentication.simple.principal import PrincipalBase

from z3c.configurator import configurator
from z3c.form import form, field, button
from z3c.formui import layout

import grok

import mars.layer
import mars.template
import mars.view
import mars.form

from tfws.website import interfaces
from tfws.website import authentication
from tfws.website.layer import IWebsiteLayer
from tfws.website.i18n import MessageFactory as _

mars.layer.layer(IWebsiteLayer)

class WebSite(grok.Application, grok.Container):
    """Mars/Grok/Z3C demo website"""
    zope.interface.implements(interfaces.IWebSite)

    title = FieldProperty(interfaces.IWebSite['title'])
    description = FieldProperty(interfaces.IWebSite['description'])
    keyword = FieldProperty(interfaces.IWebSite['keyword'])
    body = FieldProperty(interfaces.IWebSite['body'])

    def __init__(self, title=None):
        super(WebSite, self).__init__()
        if title is not None:
            self.title = title

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.__name__)

class Index(mars.form.FormView, layout.FormLayoutSupport, form.DisplayForm):
    """Temp display view for site"""
    fields = field.Fields(interfaces.IWebSite).omit('__parent__', 'title')

class IndexTemplate(mars.template.TemplateFactory):
    grok.context(Index)
    grok.template('templates/index.pt')

class Edit(mars.form.FormView, layout.FormLayoutSupport, form.EditForm):
    """Edit form for site"""
    grok.name('edit')
    form.extends(form.EditForm)
    label = u'Tree Fern Web Site Edit Form'
    fields = field.Fields(interfaces.IWebSite).omit('__parent__')

    @button.buttonAndHandler(u'Apply and View', name='applyView')
    def handleApplyView(self, action):
        self.handleApply(self, action)
        if not self.widgets.errors:
            url = absoluteURL(self.context, self.request)
            self.request.response.redirect(url)

class Add(mars.form.FormView, layout.AddFormLayoutSupport, form.AddForm):
    """ Add form for tfws.website."""
    grok.name('add')
    grok.context(IRootFolder)
    grok.local_utility(IntIds, IIntIds) # needed for the catalog
    grok.local_utility(Catalog, ICatalog, setup=setup_catalog)

    label = _('Add a Tree Fern WebSite')
    contentName = None
    data = None

    fields = field.Fields(zope.schema.TextLine(
                                __name__='__name__',
                                title=_(u"name"),
                                required=True))

    fields += field.Fields(interfaces.IWebSite).select('title')
    fields += field.Fields(interfaces.IWebSiteMember, prefix="member").select(
        'member.login', 'member.password', 'member.firstName', 
        'member.lastName', 'member.email')

    def create(self, data):
        self.data = data
        # get form data
        title = data.get('title', u'')
        self.contentName = data.get('__name__', u'')

        # Create site
        return WebSite(title)

    def add(self, obj):
        data = self.data
        # Add the site
        if self.context.get(self.contentName) is not None:
            self.status = _('Site with name already exist.')
            self._finished_add = False
            return None
        self.context[self.contentName] = obj

        # Configure the new site
        configurator.configure(obj, data)

        self._finished_add = True
        return obj

    def nextURL(self):
        return self.request.URL[-1]

class SiteConfigurator(grok.Adapter, configurator.ConfigurationPluginBase):
    """Configure the site."""
    zope.component.adapts(interfaces.IWebSite)

    def __call__(self, data):
        # get parameters
    
        # Add the pluggable authentication utility
        sm = zope.component.getSiteManager(self.context)
        auth = SimpleAuthentication()
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(auth))
        sm['auth'] = auth
        sm.registerUtility(auth, IAuthentication)

        # setup credentials plugin
        cred = SessionCredentialsPlugin()
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(cred))
        auth[u'credentials'] = cred
        auth.credentialsPlugins += (u'credentials',)

        prm = IPrincipalRoleManager(self.context)

        # setup 'members' member container
        members = MemberContainer()
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(members))
        auth[u'members'] = members
        auth.authenticatorPlugins += (u'members',)

        # setup 'groups' group container
        groups = GroupContainer(u'groups.')
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(groups))
        auth[u'groups'] = groups
        auth.authenticatorPlugins += (u'groups',)

        # setup 'Members' group
        grp =  Group(u'Members', u'Members')
        groups.addGroup('Members', grp) 
        prm.assignRoleToPrincipal('tfws.website.Member', 'groups.Members')

        # setup 'Administrators' group
        grp =  Group(u'Administrators', u'Administrators')
        groups.addGroup('Administrators', grp) 
        prm.assignRoleToPrincipal('tfws.website.Administrator', 
            'groups.Administrators')

        # Add a Admin to the administrators group
        login = data['member.login']
        admin = authentication.WebSiteMember(login, data['member.password'], 
            data['member.firstName'], data['member.lastName'], 
            data['member.email'])
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(admin))
        auth['members'].add(admin)

        adminGroup = groups['groups.Administrators']
        adminGroup.setPrincipals(
            adminGroup.principals + (admin.__name__,), check=False)
