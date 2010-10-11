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

import transaction
import zope.interface
import zope.component
from zope.publisher.browser import BrowserPage
from zope.publisher.interfaces import NotFound
from zope.security.proxy import removeSecurityProxy
from zope.traversing.browser.absoluteurl import absoluteURL

from zope.app.pagetemplate import ViewPageTemplateFile
from zope.app.container.contained import contained

from z3c.table import column, table
from z3c.table.interfaces import IColumn as ISortableColumn
from z3c.taskqueue import interfaces

SORTED_ON_KEY = 'lovely.remotetask.service.table.sorted-on'


class CheckboxColumn(column.Column):
    """Provide a column to select applications."""

    def renderCell(self, item, formatter):
        widget = (u'<input type="checkbox" name="jobs:list" value="%i">')
        return widget % item.id


class TaskNameColumn(column.Column):
    """Provide a column for the task name and provide a link to an edit page
    is one is available."""

    def renderCell(self, item, formatter):
        view = zope.component.queryMultiAdapter((item, formatter.request),
                                                name='editjob')
        if view:
            url = absoluteURL(formatter.context, formatter.request)
            return '<a href="%s/%s/editjob">%s</a>' % (
                                                url, item.id, item.task)
        else:
            return item.task


class JobDetailColumn(column.Column):
    """Provide a column of taks input detail view."""

    def renderCell(self, item, formatter):
        view = zope.component.queryMultiAdapter((item, formatter.request),
                                              name='%s_detail' % item.task)
        if view is None:
            view = zope.component.getMultiAdapter((item, formatter.request),
                                                  name='detail')
        return view()


class StatusColumn(column.Column):
    zope.interface.implements(ISortableColumn)

    def renderCell(self, item, formatter):
        status = self.getter(item, formatter)
        cssClass = 'status-' + status
        return '<span class="%s">%s</span>' % (cssClass, status)

    def getSortKey(self, item, formatter):
        return self.getter(item, formatter)


class DatetimeColumn(column.Column):
    zope.interface.implements(ISortableColumn)

    def renderCell(self, item, formatter):
        date = self.getter(item, formatter)
        dformat = formatter.request.locale.dates.getFormatter(
            'dateTime', 'medium')
        return date and dformat.format(date) or '[not set]'

    def getSortKey(self, item, formatter):
        return self.getter(item, formatter)


class Jobs(table.Table):
    pass


class JobsOverview(BrowserPage):

    template = ViewPageTemplateFile('jobs.pt')
    status = None

    columns = (
#        CheckboxColumn(u'Sel'),
#        column.Column(u'Id', lambda x, f: str(x.id), name='id'),
#        TaskNameColumn(u'Task', name='task'),
#        StatusColumn(u'Status', lambda x, f: x.status, name='status'),
#        JobDetailColumn(u'Detail', name='detail'),
#        DatetimeColumn(u'Creation',
#                       lambda x, f: x.created, name='created'),
#        DatetimeColumn(u'Start',
#                       lambda x, f: x.started, name='start'),
#        DatetimeColumn(u'End',
#                       lambda x, f: x.completed, name='end'),
        )

    def table(self):
        return Jobs()

    def jobs(self):
        if hasattr(self, '_jobs'):
            return self._jobs

        jobs = list(self.context.jobs.values())
        jobs.reverse()
        self._jobs = jobs
        return self._jobs

    def numberOfItems(self):
        jobs = list(self.context.jobs.values())
        return len(jobs)

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
        elif 'CLEAN_ALL' in self.request:
            jobs = len(list(self.context.jobs.keys()))
            self.context.clean()
            cleaned = jobs - len(list(self.context.jobs.keys()))
            self.status = u'Cleaned %r Jobs' % cleaned
        elif 'CLEAN_ERROR' in self.request:
            jobs = len(list(self.context.jobs.keys()))
            self.context.clean(status=[interfaces.ERROR])
            cleaned = jobs - len(list(self.context.jobs.keys()))
            self.status = u'Cleaned %r Jobs' % cleaned
        elif 'CLEAN_CANCELLED' in self.request:
            jobs = len(list(self.context.jobs.keys()))
            self.context.clean(status=[interfaces.CANCELLED])
            cleaned = jobs - len(list(self.context.jobs.keys()))
            self.status = u'Cleaned %r Jobs' % cleaned
        elif 'CLEAN_COMPLETED' in self.request:
            jobs = len(list(self.context.jobs.keys()))
            self.context.clean(status=[interfaces.COMPLETED])
            cleaned = jobs - len(list(self.context.jobs.keys()))
            self.status = u'Cleaned %r Jobs' % cleaned
        elif 'CANCEL_ALL' in self.request:
            jobs = list(self.context.jobs.keys())
            for index, job in enumerate(jobs):
                if index % 100 == 99:
                    transaction.commit()
                self.context.cancel(job)
            self.status = u'All jobs cancelled'

    def __call__(self):
        self.update()
        return self.template()

from zope.publisher.interfaces import IPublishTraverse


class ServiceJobTraverser(object):
    zope.interface.implements(IPublishTraverse)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def publishTraverse(self, request, name):
        try:
            job = removeSecurityProxy(self.context.jobs[int(name)])
            # we provide a location proxy
            return contained(job, self.context, name)
        except (KeyError, ValueError):
            pass
        view = zope.component.queryMultiAdapter((self.context, request),
                                                name=name)
        if view is not None:
            return view
        raise NotFound(self.context, name, request)
