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

$Id: TextAreaWidget.py,v 1.2 2002/06/10 23:27:49 jim Exp $
"""

from Zope.App.Formulator.Widgets.Browser.BrowserWidget import BrowserWidget
from Zope.App.Formulator.Widgets.Browser.BrowserWidget import renderElement


class TextAreaWidget(BrowserWidget):
    """Textarea widget
    """
    propertyNames = BrowserWidget.propertyNames +\
                     ['width', 'height', 'extra']
    
    default = ""
    width = 80
    height = 15
    extra=""
    
    def render(self, REQUEST=None):
        return renderElement("textarea",
                             name=self.context.id,
                             css_class=self.getValue('cssClass'),
                             cols=self.getValue('width'),
                             rows=self.getValue('height'),
                             contents=self._getValueToInsert(REQUEST),
                             extra=self.getValue('extra'))
