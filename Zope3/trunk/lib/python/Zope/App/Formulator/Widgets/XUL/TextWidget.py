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

$Id: TextWidget.py,v 1.2 2002/06/10 23:27:50 jim Exp $
"""

from Zope.App.Formulator.Widgets.XUL.XULWidget import XULWidget
from Zope.App.Formulator.Widgets.XUL.XULWidget import renderElement


class TextWidget(XULWidget):
    """Text widget
    """

    __implements__ = XULWidget.__implements__

    propertyNames = XULWidget.propertyNames + \
                     ['displayMaxWidth', 'extra', 'default']

    tag = 'textbox'
    default = ''
    displayMaxWidth = ''
    extra = ''

    
    def render(self, REQUEST=None):
        """Renders this widget as HTML using property values in field.
        """
        displayMaxWidth = self.getValue('displayMaxWidth') or 0
        if displayMaxWidth > 0:
            return renderElement(self.getValue('tag'),
                                 id = self.context.id,
                                 value = self._getValueToInsert(REQUEST),
                                 cssClass = self.getValue('cssClass'),
                                 maxlength = displayMaxWidth,
                                 extra = self.getValue('extra'))
        else:
            return renderElement(self.getValue('tag'),
                                 id = self.context.id,
                                 value = self._getValueToInsert(REQUEST),
                                 cssClass = self.getValue('cssClass'),
                                 extra = self.getValue('extra'))
