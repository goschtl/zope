##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Browser widgets for items

$Id: boolwidgets.py,v 1.2 2004/05/11 11:17:12 garrett Exp $
"""
from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary

from zope.app.form.browser.widget import SimpleInputWidget, renderElement
from zope.app.form.browser.itemswidgets import RadioWidget
from zope.app.form.browser.itemswidgets import SelectWidget, DropdownWidget
from zope.app.form.interfaces import IInputWidget
from zope.app.i18n import ZopeMessageIDFactory as _

class CheckBoxWidget(SimpleInputWidget):
    """A checkbox widget used to display Bool fields.
    
    For more detailed documentation, including sample code, see
    tests/test_checkboxwidget.py.
    """
    implements(IInputWidget)
    
    type = 'checkbox'
    default = 0
    extra = ''

    def __call__(self):
        """Render the widget to HTML."""
        value = self._getFormValue()
        if value:
            kw = {'checked': None}
        else:
            kw = {}
        return "%s %s" % (
            renderElement(self.tag,
                          type='hidden',
                          name=self.name+".used",
                          id=self.name+".used",
                          value=""
                          ),
            renderElement(self.tag,
                             type=self.type,
                             name=self.name,
                             id=self.name,
                             cssClass=self.cssClass,
                             extra=self.extra,
                             **kw),
            )

    def _toFieldValue(self, input):
        """Convert from HTML presentation to Python bool."""
        return input == 'on'

    def _toFormValue(self, value):
        """Convert from Python bool to HTML representation."""
        return value and "on" or ""

    def hasInput(self):
        """Check whether the field is represented in the form."""
        return self.name + ".used" in self.request.form or \
            super(CheckBoxWidget, self).hasInput()

    def getInputValue(self):
        """Get the value from the form
        
        When it's checked, its value is 'on'.
        When a checkbox is unchecked, it does not appear in the form data."""
        value = self.request.form.get(self.name, 'off')
        return value == 'on'


def BooleanRadioWidget(field, request, true=_('on'), false=_('off')):
    vocabulary = SimpleVocabulary.fromItems( ((True, true), (False, false)) ) 
    return RadioWidget(field, vocabulary, request)


def BooleanSelectWidget(field, request, true=_('on'), false=_('off')):
    vocabulary = SimpleVocabulary.fromItems( ((True, true), (False, false)) )
    widget = SelectWidget(field, vocabulary, request)
    widget.size = 2
    return widget


def BooleanDropdownWidget(field, request, true=_('on'), false=_('off')):
    vocabulary = SimpleVocabulary.fromItems( ((True, true), (False, false)) )
    return DropdownWidget(field, vocabulary, request)
