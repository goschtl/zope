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

from zope import formlib

from zope.app.traversing.browser.absoluteurl import absoluteURL
from zope.app.publisher.browser import BrowserView

from zope.app.pagetemplate import ViewPageTemplateFile
from zope.app.form.browser.textwidgets import TextWidget

from lovely.remotetask.interfaces import CRONJOB, ICronJob


def noValidation(self, *args, **kwargs):
    return ()


class JobDetail(BrowserView):
    """A simple task input detail view."""

    def __call__(self):
        return u'No input detail available'


class CronJobDetail(BrowserView):
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

    def _toFormValue(self, input):
        if not input:
            return u''
        return u' '.join([str(v) for v in input])

    def _toFieldValue(self, input):
        if self.convert_missing_value and input == self._missing:
            value = self.context.missing_value
        else:
            value = tuple([int(v) for v in input.split()])
        return value


class CronJobEdit(formlib.form.EditForm):
    """An edit view for cron jobs."""

    form_fields = formlib.form.Fields(ICronJob).select(
            'task',
            'hour',
            'minute',
            'dayOfMonth',
            'month',
            'dayOfWeek',
            'delay',
            )
    form_fields['hour'].custom_widget = StringTupleWidget
    form_fields['minute'].custom_widget = StringTupleWidget
    form_fields['dayOfMonth'].custom_widget = StringTupleWidget
    form_fields['month'].custom_widget = StringTupleWidget
    form_fields['dayOfWeek'].custom_widget = StringTupleWidget

    inputForm = None

    base_template = formlib.form.EditForm.template
    template = ViewPageTemplateFile('cronjob.pt')

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


class AddCronJob(formlib.form.Form):
    """An edit view for cron jobs."""

    form_fields = formlib.form.Fields(
            ICronJob,
            ).select(
                'task',
                'hour',
                'minute',
                'dayOfMonth',
                'month',
                'dayOfWeek',
                'delay',
                )
    form_fields['hour'].custom_widget = StringTupleWidget
    form_fields['minute'].custom_widget = StringTupleWidget
    form_fields['dayOfMonth'].custom_widget = StringTupleWidget
    form_fields['month'].custom_widget = StringTupleWidget
    form_fields['dayOfWeek'].custom_widget = StringTupleWidget

    base_template = formlib.form.EditForm.template
    template = ViewPageTemplateFile('cronjob.pt')

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
    template = formlib.namedtemplate.NamedTemplate('default')
    actions = []

