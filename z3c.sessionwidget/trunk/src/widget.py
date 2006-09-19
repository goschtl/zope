##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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
"""Session Widget Implementation

$Id$
"""
__docformat__ = "reStructuredText"
import zope.interface
import zope.location
from zope.app import form
from zope.app.form.browser import widget
from zope.app.session.interfaces import ISession
from zope.app.session.session import SessionPkgData
from zope.schema.fieldproperty import FieldProperty

from z3c.sessionwidget import interfaces

SESSION_KEY = 'z3c.sessionwidget.SessionInputWidget'

class SessionInputWidget(widget.BrowserWidget, form.InputWidget):
    """Session Input Widget"""
    zope.interface.implements(interfaces.ISessionWidget)

    @property
    def session(self):
        """Get the session containing all data relevant for this widget."""
        return ISession(self.request)[SESSION_KEY].setdefault(
            self.name, SessionPkgData())

    def setRenderedValue(self, value):
        """See zope.app.form.interfaces.IWidget"""
        if not self.session.get('changed', False):
            self.session['data'] = value

    def hidden(self):
        """See zope.app.form.browser.interfaces.IBrowserWidget"""
        # Since the data is stored in a session, no data has to be passed here.
        return ''

    def hasInput(self):
        """See zope.app.form.interfaces.IInputWidget"""
        missing = self.context.missing_value
        return self.session.get('data', missing) is not missing

    def getInputValue(self):
        """See zope.app.form.interfaces.IInputWidget"""
        self._error = None
        field = self.context

        # form input is required, otherwise raise an error
        if not self.hasInput():
            raise MissingInputError(self.name, self.label, None)

        # Get the value from the session
        value = self.session['data']

        # allow missing values only for non-required fields
        if value == field.missing_value and not field.required:
            return value

        # value must be valid per the field constraints
        try:
            field.validate(value)
        except ValidationError, v:
            self._error = WidgetInputError(
                self.context.__name__, self.label, v)
            raise self._error

        return value

    def applyChanges(self, content):
        """See zope.app.form.interfaces.IInputWidget"""
        field = self.context
        value = self.getInputValue()
        # Look into the session to see whether the data changed
        if self.session['changed']:
            zope.location.locate(value, content, field.getName())
            field.set(content, value)
            changed = True
        else:
            changed = False
        # Cleanup the session, so that everything is reset for next time
        self.session['changed'] = None
        self.session['data'] = None
        # Now return the result
        return changed

    def __call__(self):
        """See zope.app.form.browser.interfaces.IBrowserWidget"""
        form = zope.component.getMultiAdapter(
            (self, self.request), zope.interface.Interface,
            'SessionInputWidget.form')
        form.update()
        return form.render()
