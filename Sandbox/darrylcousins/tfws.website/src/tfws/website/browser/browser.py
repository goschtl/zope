from zope.traversing.browser import absoluteURL
from zope.app.folder.interfaces import IRootFolder
from zope.dublincore.interfaces import IZopeDublinCore
from zope.traversing import api

from z3c.form import form, field

from zc.table import column
from zc.table import table

import grok

import mars.layer
import mars.view
import mars.template

from tfws.website import interfaces
from tfws.website.browser import formatter
from tfws.website.layer import IWebSiteLayer
from tfws.website.i18n import MessageFactory as _

mars.layer.layer(IWebSiteLayer)

# rremove this defintion
grok.define_permission('tfws.ManageSites')

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
    grok.require('tfws.ManageSites')

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
    

