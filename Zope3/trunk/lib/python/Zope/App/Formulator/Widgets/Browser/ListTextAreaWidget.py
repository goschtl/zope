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

$Id: ListTextAreaWidget.py,v 1.2 2002/06/10 23:27:49 jim Exp $
"""

from Zope.App.Formulator.Widgets.Browser.TextAreaWidget import TextAreaWidget
from Zope.App.Formulator.Widgets.Browser.BrowserWidget import renderElement


class ListTextAreaWidget(TextAreaWidget):
    """ListTextArea widget
    """

    __implements__ = TextAreaWidget.__implements__

    propertyNames = TextAreaWidget.propertyNames + \
                     ['extra', 'default']

    default = []
    extra = ''

    
    def render(self, REQUEST=None):
        """Renders this widget as HTML using property values in field.
        """
        lines = []
        for element_text, element_value in value:
            lines.append("%s | %s" % (element_text, element_value))
        return Widget.TextAreaWidget.render(self, field, key,
                                            string.join(lines, '\n'),
                                            REQUEST)
