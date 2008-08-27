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
"""Spreadsheet Implementation

$Id$
"""
__docformat__ = "reStructuredText"
import zope.interface
from zope.session.interfaces import ISession
from z3c.form import button, field, form, interfaces
from z3c.formui import layout
from zc.table import table, column

from z3c.formdemo.browser import formatter
from z3c.formdemo.spreadsheet import content


class SpreadsheetDataColumn(column.SortingColumn):

    def __init__(self, field):
        super(SpreadsheetDataColumn, self).__init__(field.title, field.__name__)

    def renderCell(self, item, formatter):
        return item.widgets[self.name].render()

    def getSortKey(self, item, formatter):
        return item.widgets[self.name].value


class SpreadsheetActionsColumn(column.Column):

    def __init__(self):
        super(SpreadsheetActionsColumn, self).__init__(
            u'Actions', 'actions')

    def renderCell(self, item, formatter):
        return '\n'.join(
            [action.render() for action in item.actions.values()] )


class AddRow(form.AddForm):
    form.extends(form.AddForm)
    prefix = 'add.'

    def __init__(self, spreadsheet):
        super(AddRow, self).__init__(spreadsheet.context, spreadsheet.request)
        self.fields = spreadsheet.rowFields
        self.sessionKey = spreadsheet.sessionKey

    def create(self, data):
        return content.Candidate(**data)

    def add(self, object):
        count = 0
        while 'candidate-%i' %count in self.context:
            count += 1;
        self._name = 'candidate-%i' %count
        self.context[self._name] = object
        return object

    def update(self):
        super(AddRow, self).update()
        if self._finishedAdd:
            # Purposefully do not deactivate add-mode, so that multiple
            # candidates can be added at once.
            self.request.response.redirect(self.request.getURL())

    @button.buttonAndHandler(u'Cancel')
    def handleCancel(self, action):
        ISession(self.request)[self.sessionKey]['add'] = False
        self.request.response.redirect(self.request.getURL())


class EditRow(form.EditForm):

    def __init__(self, spreadsheet, content):
        super(EditRow, self).__init__(spreadsheet.context, spreadsheet.request)
        self.fields = spreadsheet.rowFields
        self.content = content
        self.prefix = str(content.__name__) + '.'
        self.sessionKey = spreadsheet.sessionKey

    @property
    def edit(self):
        name = ISession(self.request)[self.sessionKey].get('edit')
        return self.content.__name__ == name

    def getContent(self):
        return self.content

    def updateWidgets(self):
        self.widgets = zope.component.getMultiAdapter(
            (self, self.request, self.getContent()), interfaces.IWidgets)
        if not self.edit:
            self.widgets.mode = interfaces.DISPLAY_MODE
        self.widgets.update()

    @button.buttonAndHandler(u'Edit', condition=lambda form: not form.edit)
    def handleEdit(self, action):
        ISession(self.request)[self.sessionKey]['edit'] = self.content.__name__
        self.request.response.redirect(self.request.getURL())

    @button.buttonAndHandler(u'Save', condition=lambda form: form.edit)
    def handleSave(self, action):
        self.handleApply(self, action)
        if not self.widgets.errors:
            ISession(self.request)[self.sessionKey]['edit'] = None
            self.request.response.redirect(self.request.getURL())

    @button.buttonAndHandler(u'Cancel', condition=lambda form: form.edit)
    def handleCancel(self, action):
        ISession(self.request)[self.sessionKey]['edit'] = None
        self.request.response.redirect(self.request.getURL())


class Spreadsheet(layout.FormLayoutSupport, form.Form):

    sessionKey = 'z3c.formdemo.spreadsheet'
    rowFields = None
    columnWidths = None

    @property
    def add(self):
        return ISession(self.request)[self.sessionKey].get('add', False)

    @button.buttonAndHandler(u'Add', condition=lambda form: not form.add)
    def handleAdd(self, action):
        ISession(self.request)[self.sessionKey]['add'] = True
        self.updateActions()

    def update(self):
        super(Spreadsheet, self).update()

        rows = []
        for candidate in self.getContent():
            row = EditRow(self, candidate)
            row.update()
            rows.append(row)

        if self.add:
            row = AddRow(self)
            row.update()
            rows.append(row)

        columns = [SpreadsheetDataColumn(field.field)
                   for field in self.rowFields.values()]
        columns.append(SpreadsheetActionsColumn())

        self.table = formatter.SelectedItemFormatter(
            self.context, self.request, rows,
            prefix = self.sessionKey + '.', columns=columns,
            sort_on=[('lastName', False)])
        self.table.sortKey = 'formdemo.spreadsheet.sort-on'
        self.table.widths = self.columnWidths + (100,)
