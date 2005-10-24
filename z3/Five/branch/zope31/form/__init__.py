##############################################################################
#
# Copyright (c) 2004, 2005 Zope Corporation and Contributors.
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
"""Add and edit views

$Id$
"""
import sys
from datetime import datetime

import Acquisition
import transaction
from zope.event import notify
from zope.schema.interfaces import ValidationError
from zope.publisher.browser import isCGI_NAME
from zope.i18n.interfaces import IUserPreferredCharsets

from zope.app.form.browser.editview import EditView as zope_app_EditView
from zope.app.location.interfaces import ILocation
from zope.app.location import LocationProxy
from zope.app.form.utility import setUpEditWidgets, applyWidgetsChanges
from zope.app.form.browser.submit import Update
from zope.app.form.interfaces import WidgetsError, MissingInputError
from zope.app.form.utility import setUpWidgets, getWidgetsData
from zope.app.form.interfaces import IInputWidget, WidgetsError
from zope.app.event.objectevent import ObjectCreatedEvent, ObjectModifiedEvent
from zope.app.i18n import ZopeMessageFactory as _

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

class EditView(zope_app_EditView):
    generated_form = ZopeTwoPageTemplateFile('edit.pt')

    def __init__(self, context, request):
        self._processInputs()
        self._setPageEncoding()
        super(EditView, self).__init__(context, request)

    # taken from zope.publisher.browser.BrowserRequest
    def _decode(self, text):
        """Try to decode the text using one of the available charsets."""
        if self.charsets is None:
            envadapter = IUserPreferredCharsets(self.request)
            self.charsets = envadapter.getPreferredCharsets() or ['utf-8']
        for charset in self.charsets:
            try:
                text = unicode(text, charset)
                break
            except UnicodeError:
                pass
        return text
    
    def _processInputs(self):
        request = self.request
        for name, value in request.form.items():
            if (not (isCGI_NAME(name) or name.startswith('HTTP_'))
                and isinstance(value, str)):
                request.form[name] = self._decode(value)

    def _setPageEncoding(self):
        """Set the encoding of the form page via the Content-Type header.
        ZPublisher uses the value of this header to determine how to
        encode unicode data for the browser."""
        envadapter = IUserPreferredCharsets(self.request)
        charsets = envadapter.getPreferredCharsets() or ['utf-8']
        self.request.RESPONSE.setHeader(
            'Content-Type', 'text/html; charset=%s' % charsets[0])

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

        if self.request.form.has_key(Update):

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
        # hack to please typical Zope 2 factories, which expect id and title
        args = ('tmp_id', 'Temporary title') + args
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
