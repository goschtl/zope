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
$Id$
"""
__docformat__ = "reStructuredText"
import datetime
import zope.interface
from zope.traversing.browser import absoluteURL
from zope.viewlet.viewlet import CSSViewlet

from zc.table import column
from zc.table.interfaces import ISortableColumn

from z3c.pagelet import browser
from z3c.form import button, field, form, widget
from z3c.form.interfaces import IAddForm
from z3c.formui import layout

from z3c.formdemo.browser import formatter
from z3c.formdemo.sqlmessage import interfaces, sql

SESSION_KEY = 'z3c.formdemo.sqlmessage'

SQLMessageCSSViewlet = CSSViewlet('sqlmessage.css')

DefaultDate = widget.ComputedWidgetAttribute(
    lambda adapter: datetime.date.today(),
    field=interfaces.IHelloWorld['when'], view=IAddForm)

class ISQLMessagePage(zope.interface.Interface):
    """A marker interface for all SQL Hello World pages."""

class HelloWorldAddForm(layout.AddFormLayoutSupport, form.AddForm):
    zope.interface.implements(ISQLMessagePage)

    fields = field.Fields(interfaces.IHelloWorld)

    def create(self, data):
        return data

    def add(self, data):
        data['id'] = sql.getNextId()
        data['when'] = data['when'].toordinal()
        sql.addMessage(data)
        return data

    def nextURL(self):
        url = absoluteURL(self.context, self.request)
        return url + '/showAllSQLHelloWorld.html'


class HelloWorldEditForm(layout.FormLayoutSupport, form.EditForm):
    zope.interface.implements(ISQLMessagePage)

    form.extends(form.EditForm)
    fields = field.Fields(interfaces.IHelloWorld)

    def getContent(self):
        msg = sql.getMessage(self.request.form['id'])
        content = dict(
            [(name, getattr(msg, name.upper()))
             for name in self.fields.keys()] )
        content['when'] = datetime.date.fromordinal(content['when'])
        return content

    def applyChanges(self, data):
        changed = False
        for name, value in self.getContent().items():
            if data[name] != value:
                changed = True
        data['when'] = data['when'].toordinal()
        if changed:
            id = self.request.form['id']
            sql.updateMessage(id, data)
        return changed

    @button.buttonAndHandler(u'Apply and View', name='applyView')
    def handleApplyView(self, action):
        self.handleApply(self, action)
        if not self.widgets.errors:
            url = absoluteURL(self.context, self.request)
            url += '/showSQLHelloWorld.html?id=' + self.request['id']
            self.request.response.redirect(url)


class HelloWorldDisplayForm(layout.FormLayoutSupport, form.DisplayForm):
    zope.interface.implements(ISQLMessagePage)

    fields = field.Fields(interfaces.IHelloWorld)

    def getContent(self):
        msg = sql.getMessage(self.request.form['id'])
        content = dict(
            [(name, getattr(msg, name.upper()))
             for name in self.fields.keys()] )
        content['when'] = datetime.date.fromordinal(content['when'])
        return content


class SQLColumn(column.GetterColumn):
    zope.interface.implements(ISortableColumn)

    def getter(self, item, formatter):
        return getattr(item, self.name.upper())

    def cell_formatter(self, value, item, formatter):
        return '<a href="showSQLHelloWorld.html?id=%s">%s</a>' %(
            item.ID, unicode(value))

class DateSQLColumn(SQLColumn):

    def getter(self, item, formatter):
        value = super(DateSQLColumn, self).getter(item, formatter)
        return datetime.date.fromordinal(value)

class DeleteSQLColumn(column.Column):

    def renderCell(self, item, formatter):
        link = '<a href="showAllSQLHelloWorld.html?delete=%i">[Delete]</a>'
        return link % item.ID


class HelloWorldOverview(browser.BrowserPagelet):
    zope.interface.implements(ISQLMessagePage)

    status = None

    columns = (
        SQLColumn(u'Id', name='id'),
        SQLColumn(u'Who', name='who'),
        DateSQLColumn(u'When', name='when'),
        SQLColumn(u'What', name='what'),
        DeleteSQLColumn(u'', name='delete')
        )

    def update(self):
        if 'initialize' in self.request.form:
            try:
                sql.initialize()
            except zope.rdb.DatabaseException, exc:
                self.status = "Database Message: " + exc.message
        elif 'delete' in self.request.form:
            try:
                sql.deleteMessage(self.request.form['delete'])
            except zope.rdb.DatabaseException, exc:
                self.status = "Database Message: " + exc.message

        try:
            messages = sql.queryAllMessages()
        except zope.rdb.DatabaseException, exc:
            # No message table exists yet.
            messages = ()

        self.table = formatter.ListFormatter(
            self.context, self.request, messages,
            prefix = SESSION_KEY + '.', columns=self.columns,
            sort_on=[('id', False)])
        self.table.sortKey = 'z3c.formdemo.sqlmessage.sort-on'
        self.table.cssClasses['table'] = 'message-list'
        self.table.widths = (50, 200, 100, 150, 100)
