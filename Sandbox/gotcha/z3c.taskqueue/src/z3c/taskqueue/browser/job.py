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
"""Task detail view

$Id$
"""
__docformat__ = 'restructuredtext'

from datetime import datetime

from zope import interface
from zope import component
from zope import schema
from zope.browserpage import namedtemplate

from zope import formlib

from zope.traversing.browser.absoluteurl import absoluteURL
from zope.publisher.browser import BrowserPage

from zope.app.pagetemplate import ViewPageTemplateFile
from zope.app.form.browser.textwidgets import TextWidget
from zope.app.form.browser.itemswidgets import DropdownWidget
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from lovely.remotetask.interfaces import CRONJOB, ICronJob


def noValidation(self, *args, **kwargs):
    return ()


class JobDetail(BrowserPage):
    """A simple task input detail view."""

    def __call__(self):
        return u'No input detail available'


class CronJobDetail(BrowserPage):
    """A simple task input detail view."""

    def __call__(self):
        job = self.context
        if job.scheduledFor is None:
            return u'not yet scheduled'
        if job.status == CRONJOB:
            dformat = self.request.locale.dates.getFormatter('dateTime',
                                                             'short')
        else:
            dformat = self.request.locale.dates.getFormatter('dateTime',
                                                             'medium')
        return u'Scheduled for %s'% dformat.format(job.scheduledFor)


class StringTupleWidget(TextWidget):

    values = None

    def _toFormValue(self, input):
        if not input:
            return u''
        return u' '.join([str(v) for v in input])

    def _toFieldValue(self, input):
        input = input.strip()
        if self.convert_missing_value and input == self._missing:
            return self.context.missing_value
        if self.values is not None and input == '*':
            return self.values
        return tuple([int(v) for v in input.split()])


class HourWidget(StringTupleWidget):

    values = tuple(range(0,24))


class MinuteWidget(StringTupleWidget):

    values = tuple(range(0,60))


class DayOfMonthWidget(StringTupleWidget):

    values = tuple(range(0,31))


class MonthWidget(StringTupleWidget):

    values = tuple(range(0,12))


class DayOfWeekWidget(StringTupleWidget):

    values = tuple(range(0,7))

class TaskWidget(DropdownWidget):

    def __init__(self, field, request):
        terms = [SimpleTerm(name) for name in field.context.getAvailableTasks()]
        vocabulary = SimpleVocabulary(terms)
        super(TaskWidget, self).__init__(field, vocabulary, request)

class CronJobFormBase(object):
    """base settings for all cron job forms"""

    form_fields = formlib.form.Fields(ICronJob).select(
            'task',
            'hour',
            'minute',
            'dayOfMonth',
            'month',
            'dayOfWeek',
            'delay',
            )
    form_fields['task'].custom_widget = TaskWidget
    form_fields['hour'].custom_widget = HourWidget
    form_fields['minute'].custom_widget = MinuteWidget
    form_fields['dayOfMonth'].custom_widget = DayOfMonthWidget
    form_fields['month'].custom_widget = MonthWidget
    form_fields['dayOfWeek'].custom_widget = DayOfWeekWidget

    base_template = formlib.form.EditForm.template
    template = ViewPageTemplateFile('cronjob.pt')


class CronJobEdit(formlib.form.EditForm, CronJobFormBase):
    """An edit view for cron jobs."""

    inputForm = None

    def setUpWidgets(self, ignore_request=False):
        jobtask = component.queryUtility(self.context.__parent__.taskInterface,
                                       name=self.context.task)
        if (    jobtask is not None
            and hasattr(jobtask, 'inputSchema')
            and jobtask.inputSchema is not interface.Interface
           ):
            subform = InputSchemaForm(context=self.context,
                                      request=self.request,
                                     )
            subform.prefix = 'taskinput'
            subform.form_fields = formlib.form.Fields(jobtask.inputSchema)
            self.inputForm = subform
        super(CronJobEdit, self).setUpWidgets(ignore_request=ignore_request)

    @formlib.form.action(u'Apply')
    def handle_apply_action(self, action, data):
        inputData = None
        if self.inputForm is not None:
            self.inputForm.update()
            inputData = {}
            errors = formlib.form.getWidgetsData(self.inputForm.widgets,
                                                 self.inputForm.prefix,
                                                 inputData)
            if len(inputData) == 0:
                inputData = None
        self.context.task = data['task']
        self.context.update(
                hour = data['hour'],
                minute = data['minute'],
                dayOfMonth = data['dayOfMonth'],
                month = data['month'],
                dayOfWeek = data['dayOfWeek'],
                delay = data['delay'],
                )
        self.context.__parent__.reschedule(self.context.id)

    @formlib.form.action(u'Cancel', validator=noValidation)
    def handle_cancel_action(self, action, data):
        self.request.response.redirect(self.nextURL())

    def nextURL(self):
        return '%s/@@jobs.html'% absoluteURL(self.context.__parent__,
                                             self.request)


class AddCronJob(formlib.form.Form, CronJobFormBase):
    """An edit view for cron jobs."""

    @formlib.form.action(u'Add')
    def handle_add_action(self, action, data):
        self.context.addCronJob(
                task = data['task'],
                hour = data['hour'],
                minute = data['minute'],
                dayOfMonth = data['dayOfMonth'],
                month = data['month'],
                dayOfWeek = data['dayOfWeek'],
                delay = data['delay'],
                )

    @formlib.form.action(u'Cancel', validator=noValidation)
    def handle_cancel_action(self, action, data):
        self.request.response.redirect(self.nextURL())

    def nextURL(self):
        return '%s/@@jobs.html'% absoluteURL(self.context,
                                             self.request)


class InputSchemaForm(formlib.form.AddForm):
    """An editor for input data of a job"""
    interface.implements(formlib.interfaces.ISubPageForm)
    template = namedtemplate.NamedTemplate('default')
    actions = []
