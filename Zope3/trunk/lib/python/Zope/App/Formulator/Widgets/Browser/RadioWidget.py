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

$Id: RadioWidget.py,v 1.2 2002/06/10 23:27:49 jim Exp $
"""

from SingleItemsWidget import SingleItemsWidget


class RadioWidget(SingleItemsWidget):
    """radio buttons widget.
    """
    property_names = Widget.property_names +\
                     ['first_item', 'items', 'orientation']
    
    orientation = "vertical"
                                   
    def render(self, REQUEST=None):
        rendered_items = self.render_items(field, key, value, REQUEST)
        orientation = field.get_value('orientation')
        if orientation == 'horizontal':
            return string.join(rendered_items, "&nbsp;&nbsp;")
        else:
            return string.join(rendered_items, "<br />")

        
    def render_item(self, text, value, key, css_class):
        return render_element('input',
                              type="radio",
                              css_class=css_class,
                              name=key,
                              value=value) + text
    

    def render_selected_item(self, text, value, key, css_class):
        return render_element('input',
                              type="radio",
                              css_class=css_class,
                              name=key,
                              value=value,
                              checked=None) + text
       
