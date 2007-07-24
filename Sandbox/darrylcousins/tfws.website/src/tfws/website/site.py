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
from zope.app.security.interfaces import IAuthentication
from zope.app.securitypolicy.interfaces import IRolePermissionManager

from z3c.form import form, field, button, group
from z3c.form.interfaces import IWidgets
from z3c.formui import layout
from z3c.formjs import jsaction, jsevent, jsvalidator, ajax
from z3c.configurator import configurator
from z3c.authentication.simple.authentication import SimpleAuthentication

import grok

import mars.layer
import mars.template
import mars.view
import mars.form

from tfws.website import interfaces
from tfws.website import authentication
from tfws.website import permissions
from tfws.website import roles
from tfws.website.catalog import setup_catalog
from tfws.website.layer import IWebSiteLayer
from tfws.website.i18n import MessageFactory as _

mars.layer.layer(IWebSiteLayer)

class WebSite(grok.Application, grok.Container):
    """Mars/Grok/Z3C demo website

    """
    zope.interface.implements(interfaces.IWebSite)
    grok.local_utility(IntIds, IIntIds) # needed for the catalog
    grok.local_utility(Catalog, ICatalog, setup=setup_catalog,
                       name_in_container='wcatalog')
    grok.local_utility(SimpleAuthentication, IAuthentication,
                       setup=authentication.setup_site_auth, 
                       name_in_container='auth')

    title = FieldProperty(interfaces.IWebSite['title'])
    description = FieldProperty(interfaces.IWebSite['description'])

    def __init__(self, title=u'', description=u''):
        super(WebSite, self).__init__()
        self.title = title
        self.description = description

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.__name__)

class Index(mars.view.PageletView):
    """Temp display view for site"""

    def render(self):
        """First try to locate an index page for the site"""
        for page in self.context.values():
            if interfaces.IFolderIndex.providedBy(page):
                view = zope.component.getMultiAdapter(
                        (page, self.request), name='index')
                return view(page, self.request).render()
        template = zope.component.getMultiAdapter(
            (self, self.request), self._template_interface, 
            name=self._template_name)
        return template(self)


class IndexTemplate(mars.template.TemplateFactory):
    grok.context(Index)
    grok.template('templates/index.pt')


class InitialManagerGroup(group.Group):
    label = u'Initial Manager Account'
    fields = field.Fields(interfaces.IWebSiteMember, prefix="member").select(
        'member.login', 'member.password', 'member.firstName', 
        'member.lastName', 'member.email')


class ContentMetaDataGroup(group.Group):
    label = u'Site Metadata'
    fields = field.Fields(interfaces.IWebSite).select('title', 
                                                      'description')

# try this again later
#class IEditButtons(zope.interface.Interface):
#    apply = jsaction.JSButton(title=_('Apply'))
#    applyView = jsaction.JSButton(title=_('Apply and View'))


class Edit(mars.form.FormView, layout.FormLayoutSupport, 
                               group.GroupForm, form.EditForm):
    """Edit form for site"""
    grok.name('edit')
    form.extends(form.EditForm)
    label = u'Tree Fern Web Site Edit Form'
    groups = (ContentMetaDataGroup,)

    @button.buttonAndHandler(u'Apply and View', name='applyView')
    def handleApplyView(self, action):
        self.handleApply(self, action)
        if not self.widgets.errors:
            url = absoluteURL(self.context, self.request)
            self.request.response.redirect(url)



class SiteConfigurator(grok.Adapter, configurator.ConfigurationPluginBase):
    """Configure the site, this has access to the data submitted by the add
    form as well as local utilities defined with grok.local_utility."""
    zope.component.adapts(interfaces.IWebSite)

    def __call__(self, data):
    
        auth = zope.component.getUtility(IAuthentication, 
                                         context=self.context)
        # Add a Admin to the administrators group
        login = data['member.login']
        admin = authentication.WebSiteMember(login, data['member.password'], 
            data['member.firstName'], data['member.lastName'], 
            data['member.email'])
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(admin))
        auth['members'].add(admin)

        adminGroup = auth['groups']['groups.Administrators']
        adminGroup.setPrincipals(
            adminGroup.principals + (admin.__name__,), check=False)

        # grant permissions to roles
        role_manager = IRolePermissionManager(self.context)
        role_manager.grantPermissionToRole(permissions.MANAGESITE, 
                                           roles.ADMINISTRATOR)
        role_manager.grantPermissionToRole(permissions.MANAGECONTENT, 
                                           roles.ADMINISTRATOR)
        role_manager.grantPermissionToRole(permissions.MANAGEUSERS, 
                                           roles.ADMINISTRATOR)
        role_manager.grantPermissionToRole(permissions.VIEW, 
                                           roles.ADMINISTRATOR)
        role_manager.grantPermissionToRole(permissions.MANAGECONTENT, 
                                           roles.MEMBER)
        role_manager.grantPermissionToRole(permissions.VIEW, 
                                           roles.MEMBER)
