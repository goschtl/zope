import zope.schema
import zope.event
import zope.lifecycleevent
from zope.traversing import api
from zope.app.folder.interfaces import IRootFolder
from zope.dublincore.interfaces import IZopeDublinCore
from zope.pagetemplate.interfaces import IPageTemplate
from zope.traversing.browser import absoluteURL
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from z3c.form import form, field, group, button
from z3c.formui import layout
from z3c.configurator import configurator

from zc.table import column
from zc.table import table

import grok

import mars.layer
import mars.view
import mars.template
import mars.viewlet
import mars.form

from tfws.website import interfaces
from tfws.website import permissions
from tfws.website import site
from tfws.website.browser import formatter
from tfws.website.layer import IWebSiteLayer
from tfws.website.i18n import MessageFactory as _


mars.layer.layer(IWebSiteLayer)

class CheckboxColumn(column.Column):

    def renderCell(self, item, formatter):
        widget = (u'<input type="checkbox" '
                  u'name="selected:list" value="%s">')
        return widget %api.getName(item)


def getCreatedDate(item, formatter):
    formatter = formatter.request.locale.dates.getFormatter('date', 'short')
    return formatter.format(IZopeDublinCore(item).created)


def getModifiedDate(item, formatter):
    formatter = formatter.request.locale.dates.getFormatter('date', 'short')
    return formatter.format(IZopeDublinCore(item).modified)


def link(view='index', title=''):
    def anchor(value, item, formatter):
        url = absoluteURL(item, formatter.request) + '/' + view
        return u'<a href="%s" title="%s">%s</a>' %(url, title, value)
    return anchor


class Index(mars.view.PageletView):
    grok.context(IRootFolder)
    grok.require(permissions.MANAGESITE)
    # this allows the standard http auth to get called, @@absolute_url
    # wasn't able to be rendered with Unauthorized
    # See zope.traversing.browser.absoluteurl.py
    __name__ = u'bug-fix'

    columns = (
        CheckboxColumn(_('Sel')),
        column.GetterColumn(_('Id'), 
                    lambda item, f: api.getName(item), link('index', _('View'))),
        column.GetterColumn(_('Title'), 
                    lambda item, f: item.title, link('edit', _('Edit'))),
        column.GetterColumn(_('Created On'), getCreatedDate),
        column.GetterColumn(_('Modified On'), getModifiedDate),
        )

    status = None

    def sites(self):
        return [obj
                for obj in self.context.values()
                if interfaces.IWebSite.providedBy(obj)]

    def table(self):
        formatter = table.AlternatingRowFormatter(
            self.context, self.request, self.sites(), columns=self.columns)
        formatter.widths=[25, 50, 300, 100, 100]
        formatter.cssClasses['table'] = 'list'
        return formatter()

    def update(self):
        if 'ADD' in self.request:
            self.request.response.redirect('add')
        if 'DELETE' in self.request:
            if self.request.get('confirm_delete') != 'yes':
                self.status = _('You did not confirm the deletion correctly.')
                return
            if 'selected' in self.request:
                for id in self.request['selected']:
                    del self.context[id]
                self.status = _('Sites were successfully deleted.')
            else:
                self.status = _('No sites were selected.')

class IndexTemplate(mars.template.TemplateFactory):
    """layout template for `home`"""
    grok.context(Index)
    grok.template('index.pt') 
    
class AddSite(mars.form.FormView, layout.AddFormLayoutSupport, 
                              group.GroupForm, 
                              form.AddForm):
    """ Add form for tfws.website."""
    grok.name('add')
    grok.context(IRootFolder)

    label = _('Add a Tree Fern WebSite')
    contentName = None
    data = None
    _finishedAdd = False

    fields = field.Fields(zope.schema.TextLine(__name__='__name__',
                                title=_(u"name"), required=True))

    groups = (site.ContentMetaDataGroup, site.InitialManagerGroup)

    @button.buttonAndHandler(_('Add'), name='add')
    def handleAdd(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        obj = self.create(data)
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(obj))
        result = self.add(obj)
        if result is not None:
            self._finishedAdd = True

    def create(self, data):
        self.data = data
        # get form data
        title = data.get('title', u'')
        description = data.get('description', u'')
        self.contentName = data.get('__name__', u'')

        # Create site
        return site.WebSite(title, description)

    def add(self, obj):
        data = self.data
        # Add the site
        if self.context.get(self.contentName) is not None:
            self.status = _('Site with name already exist.')
            self._finishedAdd = False
            return None
        self.context[self.contentName] = obj

        # Configure the new site
        configurator.configure(obj, data)

        self._finishedAdd = True
        return obj

    def nextURL(self):
        return self.request.URL[-1]

#from zope.security.interfaces import Unauthorized, IUnauthorized
#from zope.publisher.interfaces.http import IHTTPRequest
#from zope.traversing.browser.interfaces import IAbsoluteURL
#class AbsoluteURL(grok.MultiAdapter):
#    zope.interface.implements(IAbsoluteURL, IHTTPRequest)
#    grok.provides(IAbsoluteURL)
#    grok.adapts(IUnauthorized, IHTTPRequest)

#    def __init__(self, context, request):
#        self.context = context
#        self.context.__name__ = u'Unauthorized'
#        self.request = request

#    def __str__(self):
#        return 'I am absolute url'

#    __call__ = __str__
