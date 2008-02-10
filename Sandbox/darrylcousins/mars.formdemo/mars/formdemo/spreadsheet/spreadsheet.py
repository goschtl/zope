__docformat__ = "reStructuredText"
import zope.interface
from zope.app.session.interfaces import ISession
from z3c.form import button, field, form, interfaces
from z3c.formui import layout
from zc.table import table, column

from z3c.formdemo.browser import formatter
from z3c.formdemo.spreadsheet import content
from z3c.formdemo.spreadsheet import spreadsheet


class Spreadsheet(layout.FormLayoutSupport, form.Form):

    sessionKey = 'mars.formdemo.spreadsheet'
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
            row = spreadsheet.EditRow(self, candidate)
            row.update()
            rows.append(row)

        if self.add:
            row = spreadsheet.AddRow(self)
            row.update()
            rows.append(row)

        columns = [spreadsheet.SpreadsheetDataColumn(field.field)
                   for field in self.rowFields.values()]
        columns.append(spreadsheet.SpreadsheetActionsColumn())

        self.table = formatter.SelectedItemFormatter(
            self.context, self.request, rows,
            prefix = self.sessionKey + '.', columns=columns,
            sort_on=[('lastName', False)])
        self.table.sortKey = 'formdemo.spreadsheet.sort-on'
        self.table.widths = self.columnWidths + (100,)
