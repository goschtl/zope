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
"""Custom Widgets for the rotterdam layer.

$Id$
"""
from zope.interface import implements
from zope.app.form.interfaces import IInputWidget
from zope.app.form.browser import TextAreaWidget
from zope.app.form.browser.widget import renderElement
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

class SimpleEditingWidget(TextAreaWidget):
    """Improved textarea editing, with async saving using JavaScript."""

    implements(IInputWidget)

    default = ""
    width = 60
    height = 15
    extra=""
    style="width: 98%; font-family: monospace;"
    rowTemplate = ViewPageTemplateFile("simpleeditingrow.pt")
    rowFragment = ViewPageTemplateFile("simpleeditingrowfragment.pt")
    
    def _toFieldValue(self, value):
        if self.context.min_length and not value:
            return None
        return value

    def __call__(self):
        return renderElement("textarea",
                             name=self.name,
                             id=self.name,
                             cssClass=self.cssClass,
                             rows=self.height,
                             cols=self.width,
                             style=self.style,
                             contents=self._getFormValue(),
                             extra=self.extra)

    def contents(self):
        """Make the contents available to the template"""
        return self._getFormData()

