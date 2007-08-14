import zope.interface
import zope.component
import zope.lifecycleevent
import zope.event
from zope.traversing import api
from zope.traversing.browser import absoluteURL
from zope.app.security.interfaces import IAuthentication
from zope.app.component import hooks

from z3c.authentication.simple import member
from z3c.formui import layout
from z3c.form import form, field

from zc.table import column
from zc.table.table import AlternatingRowFormatter

import grok

import mars.view
import mars.layer
import mars.template

from tfws.website import interfaces
from tfws.website import permissions
from tfws.website import table
from tfws.website.layer import IWebSiteLayer
from tfws.website.i18n import MessageFactory as _


mars.layer.layer(IWebSiteLayer)

class Members(grok.Model):
    """Stub object generated when traversing site/members"""
    title = _('Members')

    def __init__(self, context=None):
        """Make the object locatable"""
        if not context: context = hooks.getSite()
        self.__parent__ = context
        self.__name__ = 'members'
        self.description = _("Container for site members")
        self.auth = zope.component.getUtility(IAuthentication, context=self.__parent__)

    def traverse(self, name):
        try:
            member = self.auth['members'][name]
        except KeyError:
            return
        return Member(member, parent=self)

    @property
    def members(self):
        return [obj for obj in self.auth['members'].values()
                    if interfaces.IWebSiteMember.providedBy(obj)]

    def deleteMember(self, id):
        del self.auth['members'][id]


def link(view='index', title=''):
    def anchor(value, item, formatter):
        site = hooks.getSite()
        url = '%s/members/%s/%s' % (absoluteURL(site, formatter.request),
                                 api.getName(item), view)
        return u'<a href="%s" title="%s">%s</a>' %(url, title, value)
    return anchor


# TODO add search field, batching and sortable columns
class Index(mars.view.PageletView):
    grok.context(Members) 
    grok.require(permissions.VIEW)
    title = _("Members Folder")
    authAdd = authDelete = authActions = False

    columns = (
        table.CheckboxColumn(_('Sel')),
        column.GetterColumn(_('Id'), 
                    lambda item, f: item.login, link('index', _('View'))),
        column.GetterColumn(_('Title'), 
                    lambda item, f: item.title, link('edit', _('Edit'))),
        column.GetterColumn(_('Created On'), table.getCreatedDate),
        column.GetterColumn(_('Modified On'), table.getModifiedDate),
        )

    status = None

    def table(self):
        formatter = AlternatingRowFormatter(
            self.context, self.request, self.items, columns=self.columns)
        formatter.widths=[25, 50, 300, 100, 100]
        formatter.cssClasses['table'] = 'list'
        return formatter()

    def update(self):
        self.items = self.context.members
        if 'ADD' in self.request:
            self.request.response.redirect('add')
        if 'DELETE' in self.request:
            if self.request.get('confirm_delete') != 'yes':
                self.status = _('You did not confirm the deletion correctly.')
                return
            if 'selected' in self.request:
                for id in self.request['selected']:
                    self.context.deleteMember(login)
                self.status = _('Members were successfully deleted.')
            else:
                self.status = _('No members were selected.')

        site = hooks.getSite()
        perms = permissions.permsForPrincipal(site, self.request.principal)
        if permissions.MANAGEUSERS in perms:
            self.authAdd = self.authDelete = True
        self.authActions = self.authAdd and True or self.authDelete

class IndexTemplate(mars.template.TemplateFactory):
    """layout template for `home`"""
    grok.context(Index)
    grok.template('templates/contents.pt') 
    

class Member(grok.Model):
    """Stub object generated when traversing site/members"""
    grok.implements(interfaces.IWebSiteMember, interfaces.IPassword)
    verify_password = u''

    def __init__(self, context, parent=None):
        """Make the object locatable"""
        if parent == None:
            self.__parent__ = Members()
        else:
            self.__parent__ = parent
        self.__name__ = context.__name__
        self.context = context

    @property
    def email(self):
        return self.context.email

    @property
    def login(self):
        return self.context.login

    @property
    def change_password(self):
        return u''

    @property
    def verify_password(self):
        return u''

    @property
    def title(self):
        return self.context.title

    @property
    def firstName(self):
        return self.context.firstName

    @property
    def lastName(self):
        return self.context.lastName

class MemberIndex(mars.form.FormView, layout.FormLayoutSupport, 
                                                 form.DisplayForm):
    grok.name('index')
    grok.context(Member) 
    grok.require(permissions.VIEW)
    fields = field.Fields(interfaces.IWebSiteMember).select('login',
                                                           'title',
                                                           'email')
    
class MemberIndexTemplate(mars.template.TemplateFactory):
    grok.context(MemberIndex)
    grok.template('templates/member.pt') 
    
from z3c.form.interfaces import IDataManager

def applyChanges(form, content, data):
    changes = {}
    for name, field in form.fields.items():
        # If the field is not in the data, then go on to the next one
        if name not in data:
            continue
        # Get the datamanager and get the original value
        dm = zope.component.getMultiAdapter(
            (content, field.field), IDataManager)
        oldValue = dm.get()
        # Only update the data, if it is different
        if dm.get() != data[name]:
            dm.set(data[name])
            interface = dm.field.interface
            changes.setdefault(interface, []).append(name)
    return changes


class MemberEdit(mars.form.FormView, layout.FormLayoutSupport, form.EditForm):
    grok.name('edit')
    grok.context(Member) 
    grok.require(permissions.MANAGEUSERS)
    label = _('Edit Member')
    fields = field.Fields(interfaces.IWebSiteMember).select('login',
                                                           'firstName',
                                                           'lastName',
                                                           'email')
    fields += field.Fields(interfaces.IPassword)

    def applyChanges(self, data):
        content = self.getContent().context
        change_password = data.get('change_password', None)
        del data['change_password']
        del data['verify_password']

        changes = applyChanges(self, content, data)
        if content.password != change_password and change_password != None:
            content.password = change_password
            changes.setdefault(interfaces.IWebSiteMember, []).append('password')
        if changes:
            descriptions = []
            for interface, names in changes.items():
                descriptions.append(zope.lifecycleevent.Attributes(interface, 
                                            *names))
            zope.event.notify(
                zope.lifecycleevent.ObjectModifiedEvent(content, descriptions))
        return changes

