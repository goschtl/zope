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

$Id: MultiListWidget.py,v 1.2 2002/06/10 23:27:49 jim Exp $
"""

from MultiItemsWidget import MultiItemsWidget


class MultiListWidget(MultiItemsWidget):
    """List widget with multiple select.
    """
    property_names = Widget.property_names +\
                     ['items', 'size', 'extra']
    
    size = 5

    def render(self, REQUEST=None):
        rendered_items = self.render_items(field, key, value, REQUEST)

        return render_element('select',
                              name=key,
                              multiple=None,
                              css_class=field.get_value('css_class'),
                              size=field.get_value('size'),
                              contents=string.join(rendered_items, "\n"),
                              extra=field.get_value('extra'))
    
    def render_item(self, text, value, key, css_class):
        return render_element('option', contents=text, value=value)

    def render_selected_item(self, text, value, key, css_class):
        return render_element('option', contents=text, value=value,
                              selected=None)
    
MultiListWidgetInstance = MultiListWidget()
