##############################################################################
#
# Copyright (c) 2006 Lovely Systems and Contributors.
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
"""Task Service Management Views

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.publisher.browser import BrowserPage
from zope.app.pagetemplate import ViewPageTemplateFile

from z3c.table import column, table


class TaskNameColumn(column.Column):

    header = u"Task name"

    def renderCell(self, item):
        return item.task


class StatusColumn(column.Column):

    header = u"Status"

    def renderCell(self, item):
        return item.status


class DatetimeColumn(column.Column):

    header = u"Created"

    def renderCell(self, item):
        date = item.created
        dformat = self.request.locale.dates.getFormatter(
            'dateTime', 'medium')
        return date and dformat.format(date) or '[not set]'


class JobsTable(table.SequenceTable):

    def setUpColumns(self):
        firstColumn = TaskNameColumn(self.context, self.request, self)
        firstColumn.__name__ = u'taskname'
        firstColumn.weight = 1
        secondColumn = StatusColumn(self.context, self.request, self)
        secondColumn.__name__ = u'status'
        secondColumn.weight = 2
        thirdColumn = DatetimeColumn(self.context, self.request, self)
        thirdColumn.__name__ = u'datetime'
        thirdColumn.weight = 3
        return [firstColumn, secondColumn, thirdColumn]


class JobsOverview(BrowserPage):

    template = ViewPageTemplateFile('jobs.pt')

    def table(self):
        if not hasattr(self, '_table'):
            self._table = JobsTable(self.jobs(), self.request)
        return self._table

    def jobs(self):
        if not hasattr(self, '_jobs'):
            jobs = list(self.context.jobs.values())
            jobs.reverse()
            self._jobs = jobs
        return self._jobs

    def __call__(self):
        self.table().update()
        return self.template()
