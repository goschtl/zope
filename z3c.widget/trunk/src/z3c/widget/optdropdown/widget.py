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
"""Optional Dropdown Widget

$Id$
"""
__docformat__ = "reStructuredText"
import zope.component
from zope.app import form
from zope.app.form import browser

class OptionalDropdownWidget(object):
    """Optional Dropdown Widget"""
    zope.interface.implements(browser.interfaces.IBrowserWidget,
                              form.interfaces.IInputWidget)

    connector = u'<br />\n'

    _prefix = 'field.'

    # See zope.app.form.interfaces.IWidget
    name = None
    label = property(lambda self: self.context.title)
    hint = property(lambda self: self.context.description)
    visible = True

    # See zope.app.form.interfaces.IInputWidget
    required = property(lambda self: self.context.required)

    def __init__(self, field, request):
        self.context = field
        self.request = request
        # Setup the custom value widget
        field.value_type.__name__ = 'custom'
        self.customWidget = zope.component.getMultiAdapter(
            (field.value_type, request), form.interfaces.IInputWidget)
        # Setup the dropdown widget
        self.dropdownWidget = form.browser.DropdownWidget(
            field, field.vocabulary, request)
        # Setting the prefix again, sets everything up correctly
        self.setPrefix(self._prefix)

    def setRenderedValue(self, value):
        """See zope.app.form.interfaces.IWidget"""
        if value in self.context.vocabulary:
            self.dropdownWidget.setRenderedValue(value)
            self.customWidget.setRenderedValue(
                self.context.value_type.missing_value)
        else:
            self.customWidget.setRenderedValue(value)
            self.dropdownWidget.setRenderedValue(
                self.context.missing_value)

    def setPrefix(self, prefix):
        """See zope.app.form.interfaces.IWidget"""
        # Set the prefix locally
        if not prefix.endswith("."):
            prefix += '.'
        self._prefix = prefix
        self.name = prefix + self.context.__name__
        self.customWidget.setPrefix(self.name+'.')
        self.dropdownWidget.setPrefix(self.name+'.')

    def getInputValue(self):
        """See zope.app.form.interfaces.IInputWidget"""
        if self.customWidget.hasInput():
            return self.customWidget.getInputValue()
        else:
            return self.dropdownWidget.getInputValue()

    def applyChanges(self, content):
        """See zope.app.form.interfaces.IInputWidget"""
        field = self.context
        new_value = self.getInputValue()
        old_value = field.query(content, self)
        # The selection of an existing scoresystem has not changed
        if new_value == old_value:
            return False
        field.set(content, new_value)
        return True

    def hasInput(self):
        """See zope.app.form.interfaces.IInputWidget"""
        return self.dropdownWidget.hasInput() or self.customWidget.hasInput()

    def hasValidInput(self):
        """See zope.app.form.interfaces.IInputWidget"""
        return (self.dropdownWidget.hasValidInput() or
                self.customWidget.hasValidInput())

    def hidden(self):
        """See zope.app.form.browser.interfaces.IBrowserWidget"""
        return '\n'.join((self.dropdownWidget.hidden(),
                          self.customWidget.hidden()))


    def error(self):
        """See zope.app.form.browser.interfaces.IBrowserWidget"""
        dropdownError = self.dropdownWidget.error()
        if dropdownError:
            return dropdownError
        return self.customWidget.error()


    def __call__(self):
        """See zope.app.form.browser.interfaces.IBrowserWidget"""
        return self.connector.join((self.dropdownWidget(), self.customWidget()))
