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

import zope.interface
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.publisher.browser import BrowserPage
from zc.table import column, table
from zc.table.interfaces import ISortableColumn

class CheckboxColumn(column.Column):
    """Provide a column to select applications."""

    def renderCell(self, item, formatter):
        widget = (u'<input type="checkbox" name="jobs:list" value="%i">')
        return widget %item.id

class DatetimeColumn(column.GetterColumn):
    zope.interface.implements(ISortableColumn)

    def renderCell(self, item, formatter):
        date = self.getter(item, formatter)
        dformat = formatter.request.locale.dates.getFormatter(
            'dateTime', 'short')
        return date and dformat.format(date) or '[not set]'

class JobsOverview(BrowserPage):

    template = ViewPageTemplateFile('jobs.pt')
    status = None

    columns = (
        CheckboxColumn(u'Sel'),
        column.GetterColumn(u'Id', lambda x, f: str(x.id), name='id'),
        column.GetterColumn(u'Task', lambda x, f: x.task, name='task'),
        column.GetterColumn(u'Status', lambda x, f: x.status, name='status'),
        DatetimeColumn(u'Creation Date',
                       lambda x, f: x.created, name='created'),
        DatetimeColumn(u'Start Date',
                       lambda x, f: x.started, name='start'),
        DatetimeColumn(u'Completion Date',
                       lambda x, f: x.completed, name='completed'),
        )

    def table(self):
        formatter = table.StandaloneFullFormatter(
            self.context, self.request, self.context.jobs.values(),
            prefix='jobs.', columns=self.columns)
        return formatter()

    def getAvailableTasks(self):
        return sorted(self.context.getAvailableTasks().keys())

    def update(self):
        if 'STARTPROCESSING' in self.request:
            self.context.startProcessing()
        elif 'STOPPROCESSING' in self.request:
            self.context.stopProcessing()
        elif 'CANCEL' in self.request:
            if 'jobs' in self.request:
                for id in self.request['jobs']:
                    self.context.cancel(int(id))
                self.status = 'Jobs were successfully cancelled.'
            else:
                self.status = u'No jobs were selected.'
        elif 'CLEAN' in self.request:
            jobs = len(list(self.context.jobs.keys()))
            self.context.clean()
            cleaned = jobs - len(list(self.context.jobs.keys()))
            self.status = u'Cleaned %r Jobs' % cleaned

    def __call__(self):
        self.update()
        return self.template()
