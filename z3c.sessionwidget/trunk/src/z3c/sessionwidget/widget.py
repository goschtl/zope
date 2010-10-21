##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
from zope.app.form.interfaces import WidgetInputError, MissingInputError
from zope.schema.interfaces import ValidationError
from zope.security.proxy import removeSecurityProxy
import sha

SESSION_KEY = 'z3c.sessionwidget.SessionInputWidget'

class SessionInputWidget(widget.BrowserWidget, form.InputWidget):
    """Session Input Widget"""
    zope.interface.implements(interfaces.ISessionWidget)

    @property
    def sessionKey(self):
        if self.request._traversed_names:
            key = '/'.join(self.request._traversed_names[:-1] + \
                           [self.name])
        else:
            key = self.name
        key = sha.new(key).hexdigest()
        return key

    @property
    def session(self):
        """Get the session containing all data relevant for this
        widget."""
        # key from url of context
        return ISession(self.request)[SESSION_KEY].setdefault(
            self.sessionKey, SessionPkgData())

    def setRenderedValue(self, value):
        """See zope.app.form.interfaces.IWidget"""
        if not self.session.get('changed', False):
            # we need to remove the security proxy here to pickle the
            # object
            value = removeSecurityProxy(value)
            self.session['data'] = value            

    def hidden(self):
        """See zope.app.form.browser.interfaces.IBrowserWidget"""
        # Since the data is stored in a session, no data has to be passed here.
        usedMarker = widget.renderElement('input',
                                          type='hidden',
                                          name=self.name+".used",
                                          id=self.name+".used",
                                          value=""
                                          )
        return usedMarker

    def hasInput(self):
        """Check whether the field is represented in the form."""
        return self.name + ".used" in self.request.form

    def getInputValue(self):
        """See zope.app.form.interfaces.IInputWidget"""
        self._error = None
        field = self.context

        # form input is required, otherwise raise an error
        if not self.hasInput():
            raise MissingInputError(self.name, self.label, None)

        # Get the value from the session
        value = self.session.get('data', field.missing_value)

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
        """See zope.app.form.interfaces.IInputWidget
        this method is not used by formlib !!
        XXX test this
        """
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
            (self, self.request), name='SessionInputWidget.form')
        form.update()
        return self.hidden() + form.render()
