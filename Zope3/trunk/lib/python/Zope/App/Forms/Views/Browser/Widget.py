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
$Id: Widget.py,v 1.10 2002/10/28 23:52:31 jim Exp $
"""
from types import ListType, TupleType
ListTypes = (ListType, TupleType)
from Zope.App.Forms import Converter
from Zope.ComponentArchitecture import getAdapter
from Zope.Proxy.ProxyIntrospection import removeAllProxies
from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.App.Forms.Views.Browser.IBrowserWidget import IBrowserWidget
from Zope.App.Forms.Converter import \
     NoneToEmptyListConverter, ValueToSingleItemListConverter
from Zope.App.Forms.Widget import Widget
from Zope.App.Forms.Converter import StrToIntConverter, StrToFloatConverter


class BrowserWidget(Widget, BrowserView):
    """A field widget that knows how to display itself as HTML."""

    __implements__ = IBrowserWidget
    converter = Converter.NullConverter()

    propertyNames = (Widget.propertyNames + 
                     ['tag', 'type', 'cssClass', 'extra'])
    
    tag = 'input'
    type = 'text'
    cssClass = ''
    extra = ''
    _data = ''
    _prefix = 'field.'

    def setPrefix(self, prefix):
        if not prefix.endswith("."):
            prefix += '.'
        self._prefix = prefix
    
    def _getRawData(self):
        return self.request.form[self._prefix + self.context.__name__] 

    def _convert(self, value):
        return self.converter.convert(value)

    def setData(self, value):
        self._data = value

    def __call__(self):
        'See Zope.App.Forms.Views.Browser.IBrowserWidget.IBrowserWidget'
        return renderElement(self.getValue('tag'),
                             type = self.getValue('type'),
                             name = self._prefix + self.context.__name__,
                             value = self._data,
                             cssClass = self.getValue('cssClass'),
                             extra = self.getValue('extra'))

    def hidden(self):
        'See Zope.App.Forms.Views.Browser.IBrowserWidget.IBrowserWidget'
        return renderElement(self.getValue('tag'),
                             type = 'hidden',
                             name = self._prefix + self.context.__name__,
                             value = self._data,
                             cssClass = self.getValue('cssClass'),
                             extra = self.getValue('extra'))
        


    def render(self, value):
        'See Zope.App.Forms.Views.Browser.IBrowserWidget.IBrowserWidget'
        self.setData(value)
        return self()

    def renderHidden(self, value):
        'See Zope.App.Forms.Views.Browser.IBrowserWidget.IBrowserWidget'
        self.setData(value)
        return self.hidden()


class CheckBoxWidget(BrowserWidget):
    """Checkbox widget"""
    propertyNames = BrowserWidget.propertyNames + \
                     ['extra', 'default']

    type = 'checkbox'
    default = 0
    extra = ''

    def __call__(self):
        'See Zope.App.Forms.Views.Browser.IBrowserWidget.IBrowserWidget'
        if self._data:
            return renderElement(self.getValue('tag'),
                                 type = self.getValue('type'),
                                 name = self._prefix + self.context.__name__,
                                 checked = None,
                                 cssClass = self.getValue('cssClass'),
                                 extra = self.getValue('extra'))
        else:
            return renderElement(self.getValue('tag'),
                                 type = self.getValue('type'),
                                 name = self._prefix + self.context.__name__,
                                 cssClass = self.getValue('cssClass'),
                                 size = self.getValue('displayWidth'),
                                 extra = self.getValue('extra'))


class TextWidget(BrowserWidget):
    """Text widget."""
    propertyNames = BrowserWidget.propertyNames + \
                     ['displayWidth', 'displayMaxWidth', 'extra', 'default']
    default = ''
    displayWidth = 20
    displayMaxWidth = ""
    extra = ''

    def __call__(self):
        'See Zope.App.Forms.Views.Browser.IBrowserWidget.IBrowserWidget'
        displayMaxWidth = self.getValue('displayMaxWidth') or 0
        if displayMaxWidth > 0:
            return renderElement(self.getValue('tag'),
                                 type = self.getValue('type'),
                                 name = self._prefix + self.context.__name__,
                                 value = self._data,
                                 cssClass = self.getValue('cssClass'),
                                 size = self.getValue('displayWidth'),
                                 maxlength = displayMaxWidth,
                                 extra = self.getValue('extra'))
        else:
            return renderElement(self.getValue('tag'),
                                 type = self.getValue('type'),
                                 name = self._prefix + self.context.__name__,
                                 value = self._data,
                                 cssClass = self.getValue('cssClass'),
                                 size = self.getValue('displayWidth'),
                                 extra = self.getValue('extra'))

class BytesWidget(TextWidget):

    def _convert(self, value):
        if type(value) is unicode:
            value = value.encode('ascii')

        return value

class IntWidget(TextWidget):
    displayWidth = 10

    converter = StrToIntConverter()

class FloatWidget(TextWidget):
    displayWidth = 10

    converter = StrToFloatConverter()

class TextAreaWidget(BrowserWidget):
    """Textarea widget."""
    propertyNames = BrowserWidget.propertyNames +\
                     ['width', 'height', 'extra']
    
    default = ""
    width = 80
    height = 15
    extra=""
    
    def __call__(self):
        'See Zope.App.Forms.Views.Browser.IBrowserWidget.IBrowserWidget'
        return renderElement("textarea",
                             name = self._prefix + self.context.__name__,
                             cssClass = self.getValue('cssClass'),
                             cols = self.getValue('width'),
                             rows = self.getValue('height'),
                             contents = self._data,
                             extra = self.getValue('extra'))


class PasswordWidget(TextWidget):
    """Password Widget"""
    type='password'


class FileWidget(TextWidget):
    """File Widget"""
    converter = Converter.FileToStrConverter()
    type = 'file'

    def __call__(self):
        'See Zope.App.Forms.Views.Browser.IBrowserWidget.IBrowserWidget'
        displayMaxWidth = self.getValue('displayMaxWidth') or 0
        if displayMaxWidth > 0:
            return renderElement(self.getValue('tag'),
                                 type = self.getValue('type'),
                                 name = self._prefix + self.context.__name__,
                                 cssClass = self.getValue('cssClass'),
                                 size = self.getValue('displayWidth'),
                                 maxlength = displayMaxWidth,
                                 extra = self.getValue('extra'))
        else:
            return renderElement(self.getValue('tag'),
                                 type = self.getValue('type'),
                                 name = self._prefix + self.context.__name__,
                                 cssClass = self.getValue('cssClass'),
                                 size = self.getValue('displayWidth'),
                                 extra = self.getValue('extra'))


class ItemsWidget(BrowserWidget):
    """A widget that has a number of items in it."""
    items = []


class SingleItemsWidget(ItemsWidget):
    """A widget with a number of items that has only a single
    selectable item."""
    default = ""
    firstItem = 0    

    def renderItems(self, value):
        name = self._prefix + self.context.__name__
        # get items
        items = self.context.items
        if callable(items):
            items = items()
        # check if we want to select first item
        if not value and getattr(self.context, 'firstItem', None) and \
               len(items) > 0:
            try:
                text, value = items[0]
            except ValueError:
                value = items[0]
                
        cssClass = self.getValue('cssClass')
        
        # FIXME: what if we run into multiple items with same value?
        rendered_items = []
        for item in items:
            try:
                item_value, item_text = item
            except ValueError:
                item_value = item
                item_text = item

            if item_value == value:
                rendered_item = self.renderSelectedItem(item_text,
                                                        item_value,
                                                        name,
                                                        cssClass)
            else:
                rendered_item = self.renderItem(item_text,
                                                item_value,
                                                name,
                                                cssClass)
                
            rendered_items.append(rendered_item)

        return rendered_items


class ListWidget(SingleItemsWidget):
    """List widget."""
    __implements__ = SingleItemsWidget.__implements__
    propertyNames = SingleItemsWidget.propertyNames +\
                     ['firstItem', 'items', 'size', 'extra']
    size = 5

    def __call__(self):
        'See Zope.App.Forms.Views.Browser.IBrowserWidget.IBrowserWidget'
        renderedItems = self.renderItems(self._data)
        return renderElement('select',
                              name = self._prefix + self.context.__name__,
                              cssClass = self.getValue('cssClass'),
                              size = self.getValue('size'),
                              contents = "\n".join(renderedItems),
                              extra = self.getValue('extra'))

    def renderItem(self, text, value, name, cssClass):
        return renderElement('option', contents=text, value=value,
                              cssClass=cssClass)

    def renderSelectedItem(self, text, value, name, cssClass):
        return renderElement('option', contents=text, value=value,
                              cssClass=cssClass, selected=None)


class RadioWidget(SingleItemsWidget):
    """Radio buttons widget."""
    propertyNames = SingleItemsWidget.propertyNames +\
                     ['firstItem', 'items', 'orientation']
    orientation = "vertical"
                                   
    def __call__(self):
        'See Zope.App.Forms.Views.Browser.IBrowserWidget.IBrowserWidget'
        rendered_items = self.renderItems(self._data)
        orientation = self.getValue('orientation')
        if orientation == 'horizontal':
            return "&nbsp;&nbsp;".join(rendered_items)
        else:
            return '<br />'.join(rendered_items)

    def renderItem(self, text, value, name, cssClass):
        return renderElement('input',
                              type = "radio",
                              cssClass = cssClass,
                              name = name,
                              value = value) + text
    
    def renderSelectedItem(self, text, value, name, cssClass):
        return renderElement('input',
                              type="radio",
                              cssClass=cssClass,
                              name = name,
                              value = value,
                              checked = None) + text


class MultiItemsWidget(ItemsWidget):
    """A widget with a number of items that has multiple selectable items."""
    default = []
    converter = Converter.CombinedConverter(
        (NoneToEmptyListConverter(), ValueToSingleItemListConverter()))
        
    def renderItems(self, value):
        # need to deal with single item selects
        value = removeAllProxies(value)

        if not isinstance(value, ListTypes):
            value = [value]
        name = self._prefix + self.context.__name__
        items = self.context.items
        if callable(items):
            items = items()
        cssClass = self.getValue('cssClass')
        rendered_items = []
        for item in items:
            try:
                item_value, item_text = item
            except ValueError:
                item_value = item
                item_text = item

            if item_value in value:
                rendered_item = self.renderSelectedItem(item_text,
                                                        item_value,
                                                        name,
                                                        cssClass)
            else:
                rendered_item = self.renderItem(item_text,
                                                item_value,
                                                name,
                                                cssClass)

            rendered_items.append(rendered_item)

        return rendered_items


class MultiListWidget(MultiItemsWidget):
    """List widget with multiple select."""
    propertyNames = MultiItemsWidget.propertyNames +\
                     ['items', 'size', 'extra']
    size = 5

    def __call__(self):
        'See Zope.App.Forms.Views.Browser.IBrowserWidget.IBrowserWidget'
        rendered_items = self.renderItems(self._data)
        return renderElement('select',
                              name = self._prefix + self.context.__name__,
                              multiple = None,
                              cssClass = self.getValue('cssClass'),
                              size = self.getValue('size'),
                              contents = "\n".join(rendered_items),
                              extra = self.getValue('extra'))
    
    def renderItem(self, text, value, name, cssClass):
        return renderElement('option', contents=text, value=value)

    def renderSelectedItem(self, text, value, name, cssClass):
        return renderElement('option', contents=text, value=value,
                              selected=None)
    

class MultiCheckBoxWidget(MultiItemsWidget):
    """Multiple checkbox widget."""
    propertyNames = MultiItemsWidget.propertyNames +\
                     ['items', 'orientation']
    orientation = "vertical"
                                   
    def __call__(self):
        'See Zope.App.Forms.Views.Browser.IBrowserWidget.IBrowserWidget'
        rendered_items = self.renderItems(self._data)
        orientation = self.getValue('orientation')
        if orientation == 'horizontal':
            return "&nbsp;&nbsp;".join(rendered_items)
        else:
            return "<br />".join(rendered_items)
    
    def renderItem(self, text, value, name, cssClass):
        return renderElement('input',
                              type = "checkbox",
                              cssClass = cssClass,
                              name = name,
                              value = value) + text
    
    def renderSelectedItem(self, text, value, name, cssClass):
        return renderElement('input',
                              type = "checkbox",
                              cssClass = cssClass,
                              name = name,
                              value = value,
                              checked = None) + text


# XXX Note, some HTML quoting is needed in renderTag and renderElement.

def renderTag(tag, **kw):
    """Render the tag. Well, not all of it, as we may want to / it."""
    attr_list = []

    # special case handling for cssClass
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
