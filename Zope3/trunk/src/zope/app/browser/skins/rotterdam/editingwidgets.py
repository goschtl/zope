##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""
$Id: editingwidgets.py,v 1.1 2003/04/10 09:34:29 paul Exp $
"""

__metaclass__ = type

import sys
from types import ListType, TupleType
ListTypes = (ListType, TupleType)
from datetime import datetime
from zope.proxy.introspection import removeAllProxies
from zope.publisher.browser import BrowserView
from zope.app.interfaces.browser.form import IBrowserWidget
from zope.app.form.widget import Widget
from zope.app.interfaces.form import ConversionError, WidgetInputError
from zope.app.interfaces.form import MissingInputError
from zope.app.datetimeutils import parseDatetimetz
from zope.app.datetimeutils import DateTimeError
from zope.schema.interfaces import ValidationError
from zope.component import getService
from zope.app.browser.form.widget import PossiblyEmptyMeansMissing, BrowserWidget, renderElement
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

class SimpleEditingWidget(PossiblyEmptyMeansMissing, BrowserWidget):
    """Improved textarea editing, with async saving using JavaScript."""
    propertyNames = BrowserWidget.propertyNames + ['width', 'height', 'extra']

    default = ""
    width = 60
    height = 15
    extra=""
    style="width:100%"
    style = ''
    rowTemplate = ViewPageTemplateFile("simpleeditingrow.pt")
    rowFragment = ViewPageTemplateFile("simpleeditingrowfragment.pt")
    
    def _convert(self, value):
        if self.context.min_length and not value:
            return None
        return value

    def __call__(self):
        return renderElement("textarea",
                             name = self.name,
                             id = self.name,
                             cssClass = self.getValue('cssClass'),
#                             rows = self.getValue('height'),
#                             cols = self.getValue('width'),
#                             style = self.style,
                             contents = self._showData(),
                             extra = self.getValue('extra'))

    def contents(self):
        """Make the contents available to the template"""
        return self._showData()

    def row(self):
        # XXX This was originally set to make a colspan=2 table cell, and
        #     have the label above the text area. Perhaps we should use
        #     different div classes for this case?
        return self.rowTemplate()
        return '<h1>here</h1><div class="label">%s</div><div class="field">%s</div>' % (
                self.label(), self())
