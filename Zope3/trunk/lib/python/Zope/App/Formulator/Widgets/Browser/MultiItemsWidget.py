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

$Id: MultiItemsWidget.py,v 1.2 2002/06/10 23:27:49 jim Exp $
"""

from ItemsWidget import ItemsWidget
from types import ListType

        
class MultiItemsWidget(ItemsWidget):
    """A widget with a number of items that has multiple selectable
    items.
    """
    default = []
        
    def render_items(self, field, key, value, REQUEST):
        # need to deal with single item selects
        if not isinstance(values, ListType):
            value = [value]
        items = field.get_value('items')
        css_class = field.get_value('css_class')
        rendered_items = []
        for item in items:
            try:
                item_text, item_value = item
            except ValueError:
                item_text = item
                item_value = item

            if item_value in value:
                rendered_item = self.render_selected_item(item_text,
                                                          item_value,
                                                          key,
                                                          css_class)
            else:
                rendered_item = self.render_item(item_text,
                                                 item_value,
                                                 key,
                                                 css_class)

            rendered_items.append(rendered_item)

        return rendered_items
