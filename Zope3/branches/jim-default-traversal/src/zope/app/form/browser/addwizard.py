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
"""Add Wizard View Classes

$Id$
"""
__docformat__ = 'restructuredtext'

import sys

from zope.app import zapi
from zope.event import notify
from zope.app.event.objectevent import ObjectCreatedEvent
from zope.app.form.utility import setUpWidgets
from zope.app.form.interfaces import WidgetsError, IInputWidget
from zope.app.pagetemplate.simpleviewclass import SimpleViewClass
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.schema.interfaces import ValidationError
from zope.security.checker import defineChecker, NamesChecker
from editwizard import EditWizardView, WizardStorage

class AddWizardView(EditWizardView):
    """Multi-page add-view base class.

    Subclasses should provide a `schema` attribute defining the schema
    to be edited.
    """

    def _setUpWidgets(self):
        if self.use_session:
            # Need session for File upload fields
            raise NotImplementedError, 'Need a working ISessionDataManager'
        else:
            self.storage = WizardStorage(self.fieldNames, None)

        setUpWidgets(self, self.schema, IInputWidget, names=self.fieldNames)

    def create(self, *args, **kw):
        """Do the actual instantiation."""
        return self._factory(*args, **kw)

    def apply_update(self, data):
        """Add the desired object using the data in the data argument.

        The data argument is a dictionary with the data entered in the form.

        Issues a redirect to `context.nextURL()`

        Returns ``False``, as per `editview.apply_update`
        """

        # This code originally from add.py's createAndAdd method

        args = []
        for name in self._arguments:
            args.append(data[name])

        kw = {}
        for name in self._keyword_arguments:
            if name in data:
                kw[str(name)] = data[name]

        content = self.create(*args, **kw)
        adapted = self.schema(content)

        errors = []

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

        content = self.context.add(content)

        adapted = self.schema(content)

        for name in self._set_after_add:
            if name in data:
                field = self.schema[name]
                try:
                    field.set(adapted, data[name])
                except ValidationError:
                    errors.append(sys.exc_info()[1])

        if errors:
            raise WidgetsError(*errors)

        self.request.response.redirect(self.context.nextURL())
        return False


def AddWizardViewFactory(
    name, schema, permission, layer, panes, fields,
    template, default_template, bases, for_, content_factory, arguments,
    keyword_arguments, set_before_add, set_after_add, use_session=True):

    class_  = SimpleViewClass(template, used_for = schema, bases = bases)

    class_.schema = schema
    class_.panes = panes
    class_.fieldNames = fields
    class_._factory = content_factory
    class_._arguments = arguments or []
    class_._keyword_arguments = keyword_arguments or []
    class_._set_before_add = set_before_add or []
    class_._set_after_add = set_after_add or []
    class_.use_session = use_session

    class_.generated_form = ViewPageTemplateFile(default_template)

    defineChecker(class_,
                  NamesChecker(
                    ("__call__", "__getitem__", "browserDefault"),
                    permission,
                    )
                  )

    s = zapi.getGlobalService(zapi.servicenames.Presentation)
    s.provideView(for_, name, IBrowserRequest, class_, layer)
