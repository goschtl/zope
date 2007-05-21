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
from zope.dublincore.interfaces import IZopeDublinCore
from zope.traversing.browser import absoluteURL
from zope.traversing import api
from zc.table import column
from zc.table import table

from z3c.authentication.simple.interfaces import IMember
from z3c.configurator import configurator
from z3c.form import form
from z3c.form import field
from z3c.form import widget
from z3c.pagelet import browser
from z3c.template.interfaces import ILayoutTemplate

from z3c.website.i18n import MessageFactory as _
from z3c.website import interfaces
from z3c.website import site


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

    def sites(self):
        return [obj
                for obj in self.context.values()
                if interfaces.IWebSite.providedBy(obj)]

    def table(self):
        formatter = table.AlternatingRowFormatter(
            self.context, self.request, self.sites(), columns=self.columns)
        formatter.widths=[25, 50, 300, 100, 100]
        formatter.cssClasses['table'] = 'sorted'
        return formatter()

    def update(self):
        if 'ADD' in self.request:
            self.request.response.redirect('addZ3CWebSite.html')
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


class SiteAddPagelet(form.AddForm):

    label = _('Add WebSite')
    contentName = None
    data = None

    fields = field.Fields(
        zope.schema.TextLine(
            __name__='__name__',
            title=_(u"Name"),
            required=True))

    fields += field.Fields(interfaces.IWebSite).select('title')
    fields += field.Fields(IMember, prefix="member").select('member.title', 
        'member.description', 'member.login', 'member.password')

    def create(self, data):
        self.data = data
        # get form data
        title = data.get('title', u'')
        self.contentName = data.get('__name__', u'')

        # Create site
        return site.WebSite(title)

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

# TODO: get rid of them and implement base classes in z3c.form.pagelet.py
    def __call__(self):
        self.update()
        layout = zope.component.getMultiAdapter((self, self.request),
            ILayoutTemplate)
        return layout(self)
