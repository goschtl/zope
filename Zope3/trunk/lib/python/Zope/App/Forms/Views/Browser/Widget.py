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
$Id: Widget.py,v 1.2 2002/07/14 19:26:19 efge Exp $
"""
from types import ListTypes

from Zope.ComponentArchitecture import getAdapter
from Zope.App.Forms.Views.Browser.IBrowserWidget import IBrowserWidget
from Zope.App.Forms.IPropertyFieldAdapter import IPropertyFieldAdapter
from Zope.App.Forms.Widget import Widget


class BrowserWidget(Widget, BrowserView):
    """A field widget that knows how to display itself as HTML."""
    __implements__ = IBrowserWidget
    propertyNames = Widget.propertyNames + \
                    ['tag', 'type', 'cssClass', 'hidden', 'extra']
    
    tag = 'input'
    type = 'text'
    cssClass = ''
    hidden = 0
    extra = ''

    def _getValueToInsert(self):
        """Get a value to be inserted as the value of the input"""
        request = self.request
        field = self.context
        if request and (('field_'+field.id) in request):
            return request['field_'+field.id]
        else:
            return getAdapter(field, IPropertyFieldAdapter).\
                   getPropertyInContext()
        
            
    def render(self, field, key, value):
        'See Zope.App.Forms.Views.Browser.IBrowserWidget.IBrowserWidget'
        return renderElement(self.getValue('tag'),
                             type = self.getValue('type'),
                             name = self.context.id,
                             value = self._getValueToInsert(),
                             cssClass = self.getValue('cssClass'),
                             extra = self.getValue('extra'))


    def render_hidden(self, field, key, value):
        'See Zope.App.Forms.Views.Browser.IBrowserWidget.IBrowserWidget'
        return renderElement(self.getValue('tag'),
                             type = 'hidden',
                             name = self.context.id,
                             value = self._getValueToInsert(),
                             cssClass = self.getValue('cssClass'),
                             extra = self.getValue('extra'))


class CheckBoxWidget(BrowserWidget):
    """Checkbox widget"""
    propertyNames = BrowserWidget.propertyNames + \
                     ['extra', 'default']

    type = 'checkbox'
    default = 0
    extra = ''

    def render(self, REQUEST=None):
        'See Zope.App.Forms.Views.Browser.IBrowserWidget.IBrowserWidget'
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


class FileWidget(TextWidget):
    """File Widget"""
    type = 'file'

    def render(self, REQUEST=None):
        'See Zope.App.Forms.Views.Browser.IBrowserWidget.IBrowserWidget'
        displayMaxWidth = self.getValue('displayMaxWidth') or 0
        if displayMaxWidth > 0:
            return renderElement(self.getValue('tag'),
                                 type = self.getValue('type'),
                                 name = self.context.id,
                                 cssClass = self.getValue('cssClass'),
                                 size = self.getValue('displayWidth'),
                                 maxlength = displayMaxWidth,
                                 extra = self.getValue('extra'))
        else:
            return renderElement(self.getValue('tag'),
                                 type = self.getValue('type'),
                                 name = self.context.id,
                                 cssClass = self.getValue('cssClass'),
                                 size = self.getValue('displayWidth'),
                                 extra = self.getValue('extra'))


class ItemsWidget(Widget):
    """A widget that has a number of items in it."""
    items = []


class ListWidget(SingleItemsWidget):
    """List widget."""
    __implements__ = SingleItemsWidget.__implements__
    property_names = Widget.property_names +\
                     ['firstItem', 'items', 'size', 'extra']
    size = 5

    def render(self, REQUEST=None):
        'See Zope.App.Forms.Views.Browser.IBrowserWidget.IBrowserWidget'
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

        
class MultiItemsWidget(ItemsWidget):
    """A widget with a number of items that has multiple selectable items."""
    default = []
        
    def render_items(self, field, key, value):
        # need to deal with single item selects
        if not isinstance(values, ListTypes):
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


class MultiListWidget(MultiItemsWidget):
    """List widget with multiple select."""
    property_names = Widget.property_names +\
                     ['items', 'size', 'extra']
    size = 5

    def render(self, ):
        'See Zope.App.Forms.Views.Browser.IBrowserWidget.IBrowserWidget'
        rendered_items = self.render_items(field, key, value)

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
    

class MultiCheckBoxWidget(MultiItemsWidget):
    """Multiple checkbox widget."""
    property_names = Widget.property_names +\
                     ['items', 'orientation']
    orientation = "vertical"
                                   
    def render(self):
        'See Zope.App.Forms.Views.Browser.IBrowserWidget.IBrowserWidget'
        field = self.context
        rendered_items = self.render_items(field, key, value)
        orientation = field.get_value('orientation')
        if orientation == 'horizontal':
            return string.join(rendered_items, "&nbsp;&nbsp;")
        else:
            return string.join(rendered_items, "<br />")
    
    def render_item(self, text, value, key, css_class):
        return render_element('input',
                              type="checkbox",
                              css_class=css_class,
                              name=key,
                              value=value) + text
    
    def render_selected_item(self, text, value, key, css_class):
        return render_element('input',
                              type="checkbox",
                              css_class=css_class,
                              name=key,
                              value=value,
                              checked=None) + text


class PasswordWidget(TextWidget):
    """Password Widget"
    def render(self):
        'See Zope.App.Forms.Views.Browser.IBrowserWidget.IBrowserWidget'
        field = self.context
        display_maxwidth = field.get_value('display_maxwidth') or 0
        if display_maxwidth > 0:
            return render_element("input",
                                  type="password",
                                  name=key,
                                  css_class=field.get_value('css_class'),
                                  value=value,
                                  size=field.get_value('display_width'),
                                  maxlength=display_maxwidth,
                                  extra=field.get_value('extra'))
        else:
            return render_element("input",
                                  type="password",
                                  name=key,
                                  css_class=field.get_value('css_class'),
                                  value=value,
                                  size=field.get_value('display_width'),
                                  extra=field.get_value('extra'))


class RadioWidget(SingleItemsWidget):
    """Radio buttons widget."""
    property_names = Widget.property_names +\
                     ['first_item', 'items', 'orientation']
    orientation = "vertical"
                                   
    def render(self):
        'See Zope.App.Forms.Views.Browser.IBrowserWidget.IBrowserWidget'
        field = self.context
        rendered_items = self.render_items(field, key, value)
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


class SingleItemsWidget(ItemsWidget):
    """A widget with a number of items that has only a single
    selectable item."""
    default = ""
    first_item = 0    

    def render_items(self, field, key, value):
        # get items
        items = field.get_value('items')
    
        # check if we want to select first item
        if not value and field.get_value('first_item') and len(items) > 0:
            try:
                text, value = items[0]
            except ValueError:
                value = items[0]
                
        css_class = field.get_value('css_class')
        
        # FIXME: what if we run into multiple items with same value?
        rendered_items = []
        for item in items:
            try:
                item_text, item_value = item
            except ValueError:
                item_text = item
                item_value = item

            if item_value == value:
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


class TextAreaWidget(BrowserWidget):
    """Textarea widget."""
    propertyNames = BrowserWidget.propertyNames +\
                     ['width', 'height', 'extra']
    
    default = ""
    width = 80
    height = 15
    extra=""
    
    def render(self):
        'See Zope.App.Forms.Views.Browser.IBrowserWidget.IBrowserWidget'
        return renderElement("textarea",
                             name=self.context.id,
                             css_class=self.getValue('cssClass'),
                             cols=self.getValue('width'),
                             rows=self.getValue('height'),
                             contents=self._getValueToInsert(),
                             extra=self.getValue('extra'))


class TextWidget(BrowserWidget):
    """Text widget."""
    propertyNames = BrowserWidget.propertyNames + \
                     ['displayWidth', 'displayMaxWidth', 'extra', 'default']
    default = ''
    displayWidth = 20
    displayMaxWidth = ''
    extra = ''

    def render(self):
        'See Zope.App.Forms.Views.Browser.IBrowserWidget.IBrowserWidget'
        displayMaxWidth = self.getValue('displayMaxWidth') or 0
        if displayMaxWidth > 0:
            return renderElement(self.getValue('tag'),
                                 type = self.getValue('type'),
                                 name = self.context.id,
                                 value = self._getValueToInsert(REQUEST),
                                 cssClass = self.getValue('cssClass'),
                                 size = self.getValue('displayWidth'),
                                 maxlength = displayMaxWidth,
                                 extra = self.getValue('extra'))
        else:
            return renderElement(self.getValue('tag'),
                                 type = self.getValue('type'),
                                 name = self.context.id,
                                 value = self._getValueToInsert(REQUEST),
                                 cssClass = self.getValue('cssClass'),
                                 size = self.getValue('displayWidth'),
                                 extra = self.getValue('extra'))


# XXX Note, some HTML quoting is needed in renderTag and renderElement.

def renderTag(tag, **kw):
    """Render the tag. Well, not all of it, as we may want to / it.
    """
    attr_list = []

    kw['name'] = 'field_' + kw['name']

    # special case handling for css_class
    if 'cssClass' in kw:
        if kw['cssClass'] != "":
            attr_list.append('class="%s"' % kw['cssClass'])
        del kw['cssClass']

    # special case handling for extra 'raw' code
    if 'extra' in kw:
        extra = kw['extra'] # could be empty string but we don't care
        del kw['extra']
    else:
        extra = ""

    # handle other attributes
    for key, value in kw.items():
        if value == None:
            value = key
        attr_list.append('%s="%s"' % (key, str(value)))
            
    attr_str = " ".join(attr_list)
    return "<%s %s %s" % (tag, attr_str, extra)


def renderElement(tag, **kw):
    if 'contents' in kw:
        contents = kw['contents']
        del kw['contents']
        return "%s>%s</%s>" % (apply(renderTag, (tag,), kw), contents, tag)
    else:
        return apply(renderTag, (tag,), kw) + " />"
