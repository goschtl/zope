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

$Id: CheckBoxWidget.py,v 1.2 2002/06/10 23:27:49 jim Exp $
"""

from Zope.App.Formulator.Widgets.Browser.BrowserWidget import BrowserWidget
from Zope.App.Formulator.Widgets.Browser.BrowserWidget import renderElement


class CheckBoxWidget(BrowserWidget):
    """Text widget
    """

    __implements__ = BrowserWidget.__implements__

    propertyNames = BrowserWidget.propertyNames + \
                     ['extra', 'default']

    type = 'checkbox'
    default = 0
    extra = ''

    
    def render(self, REQUEST=None):
        """Renders this widget as HTML using property values in field.
        """
        if self._getValueToInsert(REQUEST):
            return renderElement(self.getValue('tag'),
                                 type = self.getValue('type'),
                                 name = self.context.id,
                                 checked = None,
                                 cssClass = self.getValue('cssClass'),
                                 extra = self.getValue('extra'))
        else:
            return renderElement(self.getValue('tag'),
                                 type = self.getValue('type'),
                                 name = self.context.id,
                                 cssClass = self.getValue('cssClass'),
                                 size = self.getValue('displayWidth'),
                                 extra = self.getValue('extra'))
