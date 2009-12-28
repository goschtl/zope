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
"""List Formatter Implementation

$Id$
"""
__docformat__ = "reStructuredText"
from xml.sax.saxutils import quoteattr
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.session.interfaces import ISession
from zc.table import table, column, interfaces


class ListFormatter(table.SortingFormatterMixin, table.AlternatingRowFormatter):
    """Provides a width for each column."""

    sortedHeaderTemplate = ViewPageTemplateFile('table_sorted_header.pt')

    sortKey = 'formdemo.table.sort-on'
    widths = None
    columnCSS = None

    def __init__(self, *args, **kw):
        # Figure out sorting situation
        kw['ignore_request'] = True
        request = args[1]
        prefix = kw.get('prefix')
        session = ISession(request)[self.sortKey]
        if 'sort-on' in request:
            name = request['sort-on']
            if prefix and name.startswith(prefix):
                name = name[len(prefix):]
                oldName, oldReverse = session.get(prefix, (None, None))
                if oldName == name:
                    session[prefix] = (name, not oldReverse)
                else:
                    session[prefix] = (name, False)
        # Now get the sort-on data from the session
        if prefix in session:
            kw['sort_on'] = [session[prefix]]

        super(ListFormatter, self).__init__(*args, **kw)
        self.columnCSS = {}

        self.sortOn = (None, None)
        if 'sort_on' in kw:
            for name, reverse in kw['sort_on']:
                self.columnCSS[name] = 'sorted-on'
            self.sortOn = kw['sort_on'][0]

    def getHeader(self, column):
        contents = column.renderHeader(self)
        if (interfaces.ISortableColumn.providedBy(column)):
            contents = self._wrapInSortUI(contents, column)
        return contents

    def _wrapInSortUI(self, header, column):
        name = column.name
        if self.prefix:
            name = self.prefix + name
        isSortedOn = self.sortOn[0] == column.name
        isAscending = self.sortOn[0] == column.name and not self.sortOn[1]
        isDecending = self.sortOn[0] == column.name and self.sortOn[1]
        return self.sortedHeaderTemplate(
            header=header, name=name, isSortedOn=isSortedOn,
            isAscending=isAscending, isDecending=isDecending)

    def renderContents(self):
        """Avoid to render empty table (tr) rows."""
        rows = self.renderRows()
        if not rows:
            return '  <thead%s>\n%s  </thead>\n' % (
                self._getCSSClass('thead'), self.renderHeaderRow())
        else:
            return '  <thead%s>\n%s  </thead>\n  <tbody>\n%s  </tbody>\n' % (
                self._getCSSClass('thead'), self.renderHeaderRow(),
                rows)

    def renderHeader(self, column):
        width = ''
        if self.widths:
            idx = list(self.visible_columns).index(column)
            width = ' width="%i"' %self.widths[idx]
        klass = self.cssClasses.get('tr', '')
        if column.name in self.columnCSS:
            klass += klass and ' ' or '' + self.columnCSS[column.name]
        return '      <th%s class=%s>\n        %s\n      </th>\n' % (
            width, quoteattr(klass), self.getHeader(column))


    def renderCell(self, item, column):
        klass = self.cssClasses.get('tr', '')
        if column.name in self.columnCSS:
            klass += klass and ' ' or '' + self.columnCSS[column.name]
        return '    <td class=%s>\n      %s\n    </td>\n' % (
            quoteattr(klass), self.getCell(item, column))

    def renderExtra(self):
        """Avoid use of resourcelibrary in original class."""
        return ''


class SelectedItemFormatter(ListFormatter):

    selectedItem = None

    def renderRow(self, item):
        self.row += 1
        klass = self.cssClasses.get('tr', '')
        if klass:
            klass += ' '
        if item == self.selectedItem:
            klass += 'selected'
        else:
            klass += self.row_classes[self.row % 2]

        return '  <tr class=%s>\n%s  </tr>\n' % (
            quoteattr(klass), self.renderCells(item))
