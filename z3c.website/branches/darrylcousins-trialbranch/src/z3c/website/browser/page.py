##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id: __init__.py 69382 2006-08-09 13:26:53Z rogerineichen $
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.component
from zope.component.interfaces import IFactory
from zope.dublincore.interfaces import IZopeDublinCore
from zope.traversing.browser import absoluteURL
from zope.traversing import api
from zope.app.renderer.rest import ReStructuredTextToHTMLRenderer
from zc.table import column
from zc.table import table

from z3c.configurator import configurator
from z3c.pagelet import browser
from z3c.form import form
from z3c.form import field
from z3c.form import widget
from z3c.template.interfaces import ILayoutTemplate

from z3c.website.i18n import MessageFactory as _
from z3c.website import interfaces
from z3c.website import page

#from jquery.resteditor.browser import RESTEditorFieldWidget


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


def link(view='index.html'):
    def anchor(value, item, formatter):
        url = absoluteURL(item, formatter.request) + '/' + view
        return u'<a href="%s">%s</a>' %(url, value)
    return anchor


class Overview(browser.BrowserPagelet):

    columns = (
        CheckboxColumn(_('Sel')),
        column.GetterColumn(
            _('Id'), lambda item, f: api.getName(item), link('index.html')),
        column.GetterColumn(
        _('Title'), lambda item, f: item.title, link('edit.html')),
        column.GetterColumn(_('Created On'), getCreatedDate),
        column.GetterColumn(_('Modified On'), getModifiedDate),
        )

    status = None

    def items(self):
        return [obj
                for obj in self.context.values()
                if interfaces.IPage.providedBy(obj)]

    def table(self):
        formatter = table.AlternatingRowFormatter(
            self.context, self.request, self.items(), columns=self.columns)
        formatter.widths=[25, 50, 300, 100, 100]
        formatter.cssClasses['table'] = 'list'
        return formatter()

    def update(self):
        if 'ADD' in self.request:
            self.request.response.redirect('addPage.html')
        if 'DELETE' in self.request:
            if self.request.get('confirm_delete') != 'yes':
                self.status = _('You did not confirm the deletion correctly.')
                return
            if 'selected' in self.request:
                for id in self.request['selected']:
                    del self.context[id]
                self.status = _('Pages were successfully deleted.')
            else:
                self.status = _('No pages were selected.')


class PageAddForm(form.AddForm):

    label = _('Add Page')
    factory = page.Page
    contentName = None
    data = None

    fields = field.Fields(
        zope.schema.TextLine(
            __name__='__name__',
            title=_(u"Name"),
            required=True))

    fields += field.Fields(interfaces.IPage).select('title', 'description',
        'keyword')

    def create(self, data):
        self.data = data
        # get form data
        self.contentName = data.get('__name__', u'')

        # Create site
        obj = self.factory()
        obj.title = data.get('title', u'')
        obj.description = data.get('description', u'')
        obj.keyword = data.get('keyword', u'')
        return obj

    def add(self, obj):
        
        # Add the site
        if self.context.get(self.contentName) is not None:
            self.status = _('Page with that name already exist.')
            self._finished_add = False
            return None
        self.context[self.contentName] = obj

        # Configure the new obj
        configurator.configure(obj, self.data)

        self._finished_add = True
        return obj

    def nextURL(self):
        obj = self.context[self.contentName]
        return absoluteURL(obj, self.request) + '/edit.html'

    def __call__(self):
        self.update()
        layout = zope.component.getMultiAdapter((self, self.request),
            ILayoutTemplate)
        return layout(self)


class MetaEditPagelet(form.EditForm):
    """Content edit page."""

    fields = field.Fields(interfaces.IContent).select('title', 
        'description', 'keyword')

    def __call__(self):
        self.update()
        layout = zope.component.getMultiAdapter((self, self.request),
            ILayoutTemplate)
        return layout(self)


class ContentEditPagelet(form.EditForm):
    """Content edit page."""

    fields = field.Fields(interfaces.IContent).select('body')

#    fields['body'].widgetFactory = RESTEditorFieldWidget

    def __call__(self):
        self.update()
        layout = zope.component.getMultiAdapter((self, self.request),
            ILayoutTemplate)
        return layout(self)


class IndexPage(browser.BrowserPagelet):
    """Default index view for all IPage objects."""

    @ property
    def title(self):
        return self.context.title

    @ property
    def description(self):
        return self.context.description

    @ property
    def keyword(self):
        return self.context.keyword

    @ property
    def body(self):
        body = self.context.body
        if body:
            factory = zope.component.getUtility(IFactory, 'zope.source.rest')
            source = factory(body)
            renderer = ReStructuredTextToHTMLRenderer(source, self.request)
            return renderer.render()
        else:
            return u''