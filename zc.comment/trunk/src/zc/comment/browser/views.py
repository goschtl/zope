##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Visible Source
# License, Version 1.0 (ZVSL).  A copy of the ZVSL should accompany this
# distribution.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""views for comments

$Id: views.py 5074 2006-02-06 23:54:54Z fred $
"""
from zope import interface, schema, component
import zope.cachedescriptors.property

from zope.app import zapi
from zope.app.pagetemplate import ViewPageTemplateFile

import zope.formlib.form
import zc.table.column
import zc.table.interfaces
from zc.table import table
from zope.interface.common.idatetime import ITZInfo

from zc.comment import interfaces
from zc.comment.i18n import _

class SortableColumn(zc.table.column.GetterColumn):
    interface.implements(zc.table.interfaces.ISortableColumn)

def dateFormatter(value, context, formatter):
    value = value.astimezone(ITZInfo(formatter.request))
    dateFormatter = formatter.request.locale.dates.getFormatter(
        'dateTime', length='long')
    return dateFormatter.format(value)

def principalsGetter(context, formatter):
    principals = zapi.principals()
    return [principals.getPrincipal(pid) for pid in context.principal_ids]

def principalsFormatter(value, context, formatter):
    return ', '.join([v.title for v in value])

columns = [
    SortableColumn(
        _('comment_column-date','Date'), lambda c, f: c.date, dateFormatter),
    SortableColumn(
        _('comment_column-principals', 'Principals'), principalsGetter,
        principalsFormatter),
    zc.table.column.GetterColumn( # XXX escape?
        _('comment_column-comment', 'Comment'), lambda c, f: c.body,
        cell_formatter=lambda v, i, f: unicode(v))
    ]

class Comments(zope.formlib.form.PageForm):

    label = _("Comments")

    template = ViewPageTemplateFile('comments.pt')

    form_fields = zope.formlib.form.Fields(
        interfaces.CommentText(
            __name__ = 'comment',
            title=_("New Comment"),
            ),
        )

    def setUpWidgets(self, ignore_request=False):
        super(Comments, self).setUpWidgets(ignore_request=ignore_request)
        comment = self.widgets.get('comment')
        if comment is not None:
            comment.style="width: 50ex; height: 6em;"
            comment.setRenderedValue(u'')

    @zope.cachedescriptors.property.Lazy
    def formatter(self):
        adapted = interfaces.IComments(self.context)
        factory = component.getUtility(zc.table.interfaces.IFormatterFactory)
        formatter = factory(self.context, self.request, adapted,
                            columns=columns)
        return formatter

    @zope.formlib.form.action(_("Add Comment"))
    def add(self, action, data):
        comment = data.get('comment')
        self.form_reset = True
        if comment:
            adapted = interfaces.IComments(self.context)
            adapted.add(comment)
            self.request.response.redirect(self.request.URL)

class CommentsSubPage(zope.formlib.form.SubPageForm, Comments):

    label = u''

    template = ViewPageTemplateFile('commentssub.pt')

class CommentsViewSubPage(CommentsSubPage):

    actions = form_fields = ()
