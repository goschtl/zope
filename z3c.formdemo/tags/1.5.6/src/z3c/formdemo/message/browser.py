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
"""
$Id$
"""
__docformat__ = "reStructuredText"
import datetime
from zope.traversing.browser import absoluteURL
from z3c.form import button, field, form, widget
from z3c.form.interfaces import IAddForm
from z3c.formui import layout

from z3c.formdemo.message import interfaces, message


DefaultDate = widget.ComputedWidgetAttribute(
    lambda adapter: datetime.date.today(),
    field=interfaces.IHelloWorld['when'], view=IAddForm)

class HelloWorldAddForm(layout.AddFormLayoutSupport, form.AddForm):
    """ A sample add form."""

    label = u'Hello World Message Add Form'
    fields = field.Fields(interfaces.IHelloWorld)

    def create(self, data):
        return message.HelloWorld(**data)

    def add(self, object):
        count = 0
        while 'helloworld-%i' %count in self.context:
            count += 1;
        self._name = 'helloworld-%i' %count
        self.context[self._name] = object
        return object

    def nextURL(self):
        return absoluteURL(self.context[self._name], self.request)


class HelloWorldEditForm(layout.FormLayoutSupport, form.EditForm):
    form.extends(form.EditForm)
    label = u'Hello World Message Edit Form'
    fields = field.Fields(interfaces.IHelloWorld)

    @button.buttonAndHandler(u'Apply and View', name='applyView')
    def handleApplyView(self, action):
        self.handleApply(self, action)
        if not self.widgets.errors:
            url = absoluteURL(self.context, self.request)
            self.request.response.redirect(url)


class HelloWorldDisplayForm(layout.FormLayoutSupport, form.DisplayForm):
    fields = field.Fields(interfaces.IHelloWorld)
