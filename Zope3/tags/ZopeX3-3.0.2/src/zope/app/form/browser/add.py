##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Add Form View class

$Id$
"""
__docformat__ = 'restructuredtext'

import sys

from zope.app import zapi
from zope.event import notify
from zope.app.event.objectevent import ObjectCreatedEvent
from zope.app.form.utility import setUpWidgets, getWidgetsData
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.form.interfaces import IInputWidget, WidgetsError
from zope.app.pagetemplate.simpleviewclass import SimpleViewClass
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.schema.interfaces import ValidationError
from zope.security.checker import defineChecker, NamesChecker
from zope.app.publisher.browser.globalbrowsermenuservice import \
    globalBrowserMenuService
from editview import EditView
from submit import Update

class AddView(EditView):
    """Simple edit-view base class.

    Subclasses should provide a schema attribute defining the schema
    to be edited.
    """

    def _setUpWidgets(self):
        setUpWidgets(self, self.schema, IInputWidget, names=self.fieldNames)

    def update(self):

        if self.update_status is not None:
            # We've been called before. Just return the previous result.
            return self.update_status

        if Update in self.request:

            self.update_status = ''
            try:
                data = getWidgetsData(self, self.schema, names=self.fieldNames)
                self.createAndAdd(data)
            except WidgetsError, errors:
                self.errors = errors
                self.update_status = _("An error occured.")
                return self.update_status

            self.request.response.redirect(self.nextURL())

        return self.update_status

    def create(self, *args, **kw):
        """Do the actual instantiation."""
        return self._factory(*args, **kw)

    def createAndAdd(self, data):
        """Add the desired object using the data in the data argument.

        The data argument is a dictionary with the data entered in the form.
        """

        args = []
        if self._arguments:
            for name in self._arguments:
                args.append(data[name])

        kw = {}
        if self._keyword_arguments:
            for name in self._keyword_arguments:
                if name in data:
                    kw[str(name)] = data[name]

        content = self.create(*args, **kw)
        adapted = self.schema(content)

        errors = []

        if self._set_before_add:
            for name in self._set_before_add:
                if name in data:
                    field = self.schema[name]
                    try:
                        field.set(adapted, data[name])
                    except ValidationError:
                        errors.append(sys.exc_info()[1])

        if errors:
            raise WidgetsError(*errors)

        notify(ObjectCreatedEvent(content))

        content = self.add(content)

        adapted = self.schema(content)

        if self._set_after_add:
            for name in self._set_after_add:
                if name in data:
                    field = self.schema[name]
                    try:
                        field.set(adapted, data[name])
                    except ValidationError:
                        errors.append(sys.exc_info()[1])

        if errors:
            raise WidgetsError(*errors)

        return content

    def add(self, content):
        return self.context.add(content)

    def nextURL(self):
        return self.context.nextURL()


def AddViewFactory(name, schema, label, permission, layer,
                   template, default_template, bases, for_,
                   fields, content_factory, arguments,
                   keyword_arguments, set_before_add, set_after_add,
                   menu=u''):

    s = zapi.getGlobalService(zapi.servicenames.Presentation)
    class_  = SimpleViewClass(
        template,
        used_for = schema, bases = bases
        )

    class_.schema = schema
    class_.label = label
    class_.fieldNames = fields
    class_._factory = content_factory
    class_._arguments = arguments
    class_._keyword_arguments = keyword_arguments
    class_._set_before_add = set_before_add
    class_._set_after_add = set_after_add

    class_.generated_form = ViewPageTemplateFile(default_template)

    defineChecker(class_,
                  NamesChecker(
                    ("__call__", "__getitem__",
                     "browserDefault", "publishTraverse"),
                    permission,
                    )
                  )

    s.provideView(for_, name, IBrowserRequest, class_, layer)
