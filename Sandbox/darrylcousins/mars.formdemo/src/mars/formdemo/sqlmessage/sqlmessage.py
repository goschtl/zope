import datetime

import zope.interface
import zope.rdb
from zope.traversing.browser import absoluteURL
from zope.viewlet.viewlet import CSSViewlet

from zc.table import column
from zc.table.interfaces import ISortableColumn

from z3c.form import widget, field, form, button
from z3c.form.interfaces import IAddForm
from z3c.formui import layout
from z3c.formdemo.sqlmessage import sql
from z3c.formdemo.browser import formatter
from z3c.formdemo.sqlmessage.interfaces import IHelloWorld
from z3c.formdemo.sqlmessage.browser import (ISQLMessagePage,
                                             SQLColumn,
                                             DateSQLColumn,
                                             DeleteSQLColumn)
                                              
import grok

import mars.form
import mars.adapter
import mars.resource
import mars.viewlet
import mars.view
import mars.layer

from mars.formdemo.layer import IDemoBrowserLayer
from mars.formdemo.skin import skin

mars.layer.layer(IDemoBrowserLayer)

SESSION_KEY = 'mars.formdemo.sqlmessage'


class DefaultDate(mars.adapter.AdapterFactory):
    grok.name('default')
    mars.adapter.factory(widget.ComputedWidgetAttribute(
                        lambda adapter: datetime.date.today(),
                        field=IHelloWorld['when'], view=IAddForm))

## CSS requirement
class MessageStyle(mars.resource.ResourceFactory):
    """File resource"""
    grok.name('sqlmessage.css')
    mars.resource.file('sqlmessage.css')

MessageCSS = CSSViewlet('sqlmessage.css')
class MessageCSSViewlet(mars.viewlet.SimpleViewlet, MessageCSS):
    """css viewlet"""
    weight = 1000
    grok.name('sqlmessage.css')
    grok.context(zope.interface.Interface)
    mars.viewlet.view(ISQLMessagePage)
    mars.viewlet.manager(skin.CSSManager)

class AddForm(mars.form.FormView, layout.AddFormLayoutSupport, form.AddForm):
    grok.context(zope.interface.Interface)
    grok.name('addsql')
    zope.interface.implements(ISQLMessagePage)

    fields = field.Fields(IHelloWorld)

    def create(self, data):
        return data

    def add(self, data):
        data['id'] = sql.getNextId()
        data['when'] = data['when'].toordinal()
        sql.addMessage(data)
        return data

    def nextURL(self):
        url = absoluteURL(self.context, self.request)
        return url + '/showallsql'

class EditForm(mars.form.FormView, layout.FormLayoutSupport, form.EditForm):
    grok.context(zope.interface.Interface)
    grok.name('editsql')
    zope.interface.implements(ISQLMessagePage)

    form.extends(form.EditForm)
    fields = field.Fields(IHelloWorld)

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
            url += '/showsql?id=' + self.request['id']
            self.request.response.redirect(url)

class DisplayForm(mars.form.FormView, layout.FormLayoutSupport, form.DisplayForm):
    grok.context(zope.interface.Interface)
    grok.name('showsql')
    zope.interface.implements(ISQLMessagePage)

    fields = field.Fields(IHelloWorld)

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
        return '<a href="showsql?id=%s">%s</a>' %(
            item.ID, unicode(value))

class DateSQLColumn(SQLColumn):

    def getter(self, item, formatter):
        value = super(DateSQLColumn, self).getter(item, formatter)
        return datetime.date.fromordinal(value)

class DeleteSQLColumn(column.Column):

    def renderCell(self, item, formatter):
        link = '<a href="showallsql?delete=%i">[Delete]</a>'
        return link % item.ID

class Overview(mars.view.PageletView):
    grok.context(zope.interface.Interface)
    grok.name('showallsql')
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

class AddFormTemplate(mars.template.TemplateFactory):
    grok.context(AddForm)
    grok.template('add.pt')

class EditFormTemplate(mars.template.TemplateFactory):
    grok.context(EditForm)
    grok.template('edit.pt')

class DisplayFormTemplate(mars.template.TemplateFactory):
    grok.context(DisplayForm)
    grok.template('display.pt')

class OverviewTemplate(mars.template.TemplateFactory):
    grok.context(Overview)
    grok.template('overview.pt')

