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

$Id: ListWidget.py,v 1.2 2002/06/10 23:27:49 jim Exp $
"""

from SingleItemsWidget import SingleItemsWidget


class ListWidget(SingleItemsWidget):
    """List widget.
    """
    __implements__ = SingleItemsWidget.__implements__

    property_names = Widget.property_names +\
                     ['firstItem', 'items', 'size', 'extra']
    size = 5

    def render(self, REQUEST=None):

        renderedItems = self.renderItems(field, key, value, REQUEST)

        return render_element('select',
                              name='',
                              cssClass=field.get_value('cssClass'),
                              size=field.get_value('size'),
                              contents=string.join(renderedItems, "\n"),
                              extra=field.get_value('extra'))

    
    def renderItem(self, text, value, key, css_class):
        return render_element('option', contents=text, value=value)


    def renderSelectedItem(self, text, value, key, css_class):
        return render_element('option', contents=text, value=value,
                              selected=None)
