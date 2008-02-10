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
from z3c.form import form, field, error

from zc.table import column
from zc.table.table import AlternatingRowFormatter

import grok

import mars.view
import mars.layer
import mars.template
import mars.adapter

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
    """Stub object generated when traversing site/members
    
    One day I would dearly like to find a way to do this set/get stuff
    with a lot less code.
    """
    grok.implements(interfaces.IWebSiteMember, interfaces.IPassword)

    def __init__(self, context, parent=None):
        """Make the object locatable"""
        if parent == None:
            self.__parent__ = Members()
        else:
            self.__parent__ = parent
        self.__name__ = context.__name__
        self.context = context

    def set_email(self, value): self.context.email = value
        
    def get_email(self): return self.context.email

    email = property(get_email, set_email)

    def set_login(self, value): self.context.login = value
        
    def get_login(self): return self.context.login

    login = property(get_login, set_login)

    def set_verify_password(self, value): pass
        
    def get_verify_password(self): return self.context.password

    verify_password = property(get_verify_password, set_verify_password)

    def set_change_password(self, value): self.context.password = value
        
    def get_change_password(self): return self.context.password

    change_password = property(get_change_password, set_change_password)

    @property
    def title(self):
        return self.context.title

    def set_firstName(self, value):
        self.context.firstName = value
        self.context.title = '%s %s' % (self.context.firstName, self.context.lastName)
        
    def get_firstName(self):
        return self.context.firstName

    firstName = property(get_firstName, set_firstName)

    def set_lastName(self, value):
        self.context.lastName = value
        self.context.title = '%s %s' % (self.context.firstName, self.context.lastName)
        
    def get_lastName(self):
        return self.context.lastName

    lastName = property(get_lastName, set_lastName)

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

# register errorViewSnippet for Invalid
# this is essential for correct rendering of the error
class PasswordErrorViewSnippet(error.InvalidErrorViewSnippet):
    """Error view snippet."""
    zope.component.adapts(
        zope.interface.Invalid, None, None, None, MemberEdit, Member)

    def __init__(self, error, request, widget, field, form, content):
        self.error = self.context = error
        self.request = request
        self.widget = form.widgets['change_password']
        self.field = form.fields['change_password']
        self.form = form
        self.content = content


class PasswordSnippet(mars.adapter.AdapterFactory):
    mars.adapter.factory(PasswordErrorViewSnippet)

