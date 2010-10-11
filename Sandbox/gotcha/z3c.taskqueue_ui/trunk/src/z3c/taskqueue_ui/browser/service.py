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

from xml.sax.saxutils import quoteattr

import transaction
import zope.interface
import zope.component
from zope.publisher.browser import BrowserPage
from zope.publisher.interfaces import NotFound
from zope.security.proxy import removeSecurityProxy
from zope.traversing.browser.absoluteurl import absoluteURL

try:
    # Newer versions of zope.app.session have deprecated IClientId,
    # so prefer to new location:
    from zope.session.interfaces import ISession
except ImportError:
    # But still support the old location if we can't get it from the new:
    from zope.app.session.interfaces import ISession

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


class ListFormatter(table.Table):
    """Provides a width for each column."""

    widths = None
    columnCSS = None
    sortable = False

    def __init__(self, *args, **kw):
        # Figure out sorting situation
        kw['ignore_request'] = True

        request = args[1]
        prefix = kw.get('prefix')

        session = zope.component.queryAdapter(request, ISession)
        if session is not None:
            self.sortable = True
            session = session[SORTED_ON_KEY]

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

    # sortable table support via session
    def getHeader(self, column):
        contents = column.renderHeader(self)
        if self.sortable and ISortableColumn.providedBy(column):
            contents = self._wrapInSortUI(contents, column)
        return contents

    def _wrapInSortUI(self, header, column):
        name = column.name
        if self.prefix:
            name = self.prefix + name
        isAscending = self.sortOn[0] == column.name and not self.sortOn[1]
        isDecending = self.sortOn[0] == column.name and self.sortOn[1]
        return self.sortedHeaderTemplate(
            header=header, name=name,
            isAscending=isAscending, isDecending=isDecending)

    def renderHeader(self, column):
        width = ''
        if self.widths:
            idx = list(self.visible_columns).index(column)
            width = ' width="%i"' % self.widths[idx]
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
        formatter = ListFormatter(
            self.context, self.request, self.jobs(),
            prefix='zc.table', columns=self.columns)
        formatter.widths = [25, 50, 100, 75, 250, 120, 120, 120]
        formatter.cssClasses['table'] = 'list'
        formatter.columnCSS['id'] = 'tableId'
        formatter.columnCSS['task'] = 'tableTask'
        formatter.columnCSS['status'] = 'tableStatus'
        formatter.columnCSS['detail'] = 'tableDetail'
        formatter.columnCSS['created'] = 'tableCreated'
        formatter.columnCSS['start'] = 'tableStart'
        formatter.columnCSS['end'] = 'tableEnd'
        return formatter()

    def jobs(self):
        if hasattr(self, '_jobs'):
            return self._jobs

        start = int(self.request.get('start', 0))
        sval = self.request.get('size', 10)
        if sval:
            size = int(sval)
        else:
            size = 10

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
