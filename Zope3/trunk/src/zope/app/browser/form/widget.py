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
$Id: widget.py,v 1.22 2003/03/20 15:05:44 mgedmin Exp $
"""

__metaclass__ = type

import sys
from types import ListType, TupleType
ListTypes = (ListType, TupleType)
from zope.proxy.introspection import removeAllProxies
from zope.publisher.browser import BrowserView
from zope.app.interfaces.browser.form import IBrowserWidget
from zope.app.form.widget import Widget
from zope.app.interfaces.form import ConversionError, WidgetInputError
from zope.app.interfaces.form import MissingInputError
from zope.schema.interfaces import ValidationError


class BrowserWidget(Widget, BrowserView):
    """A field widget that knows how to display itself as HTML."""

    __implements__ = IBrowserWidget

    propertyNames = (Widget.propertyNames +
                     ['tag', 'type', 'cssClass', 'extra'])

    tag = 'input'
    type = 'text'
    cssClass = ''
    extra = ''
    _missing = None

    def haveData(self):
        if self.name in self.request.form:
            return self._convert(self.request[self.name]) is not None
        return False

    def getData(self, optional=0):
        field = self.context
        value = self.request.form.get(self.name, self) # self used as marker
        if value is self:
            # No user input
            if field.required and not optional:
                raise MissingInputError(field.__name__, field.title,
                                        'the field is required')
            return field.default

        value = self._convert(value)
        if value is not None and not optional:

            try:
                field.validate(value)
            except ValidationError, v:
                raise WidgetInputError(self.context.__name__,
                                       self.title, str(v))

        return value

    def _convert(self, value):
        if value == self._missing:
            return None
        return value

    def _unconvert(self, value):
        if value is None:
            return ''
        return value

    def _showData(self):

        if (self._data is None):
            if self.haveData():
                data = self.getData(1)
            else:
                data = self.context.default
        else:
            data = self._data

        return self._unconvert(data)

    def __call__(self):
        return renderElement(self.getValue('tag'),
                             type = self.getValue('type'),
                             name = self.name,
                             id = self.name,
                             value = self._showData(),
                             cssClass = self.getValue('cssClass'),
                             extra = self.getValue('extra'))

    def hidden(self):
        return renderElement(self.getValue('tag'),
                             type = 'hidden',
                             name = self.name,
                             id = self.name,
                             value = self._showData(),
                             cssClass = self.getValue('cssClass'),
                             extra = self.getValue('extra'))



    def render(self, value):
        self.setData(value)
        return self()

    def renderHidden(self, value):
        self.setData(value)
        return self.hidden()

    def label(self):
        return '<label for="%s">%s</label>' % (
            self.name,
            self.title,
            )

    def row(self):
        return '<div class="label">%s</div><div class="field">%s</div>' % (
                self.label(), self())

class DisplayWidget(BrowserWidget):

    def __call__(self):
        return self._showData()

class CheckBoxWidget(BrowserWidget):
    """Checkbox widget"""
    propertyNames = BrowserWidget.propertyNames + \
                     ['extra', 'default']

    type = 'checkbox'
    default = 0
    extra = ''

    def __call__(self):
        data = self._showData()
        if data:
            kw = {'checked': None}
        else:
            kw = {}
        return renderElement(self.getValue('tag'),
                             type = self.getValue('type'),
                             name = self.name,
                             id = self.name,
                             cssClass = self.getValue('cssClass'),
                             extra = self.getValue('extra'),
                             **kw)

    def _convert(self, value):
        return value == 'on'

    def haveData(self):
        return True

    def getData(self, optional=0):
        # When it's checked, its value is 'on'.
        # When a checkbox is unchecked, it does not appear in the form data.
        field = self.context
        value = self.request.form.get(self.name, 'off')
        return value == 'on'

class PossiblyEmptyMeansMissing:

    def haveData(self):
        v = self.request.form.get(self.name)
        if v is None:
            return False
        if not v and getattr(self.context, 'min_length', 1) > 0:
            return False
        return True

    def _convert(self, value):
        v = self.request.form.get(self.name)
        if not v and getattr(self.context, 'min_length', 1) > 0:
            return None
        return v

class TextWidget(PossiblyEmptyMeansMissing, BrowserWidget):
    """Text widget."""
    propertyNames = (BrowserWidget.propertyNames +
                     ['displayWidth', 'displayMaxWidth', 'extra', 'default']
                     )
    default = ''
    displayWidth = 20
    displayMaxWidth = ""
    extra = ''
    # XXX Alex Limi doesn't like this!
    # style = "width:100%"
    style = ''
    __values = None

    def _convert(self, value):
        if self.context.min_length and not value:
            return None
        return value

    def __init__(self, *args):
        super(TextWidget, self).__init__(*args)

        if self.context.allowed_values is not None:
            values = list(self.context.allowed_values)
            values.sort()
            self.__values = values
            if values:
                self._missing = values[-1]+'x'
            else:
                self._missing = ''

    def haveData(self):
        if super(TextWidget, self).haveData():
            if (self.request.get(self.name)
                != self._missing):
                return True
        return False

    def _select(self):
        selected = self._showData()
        result = ['<select id="%s" name="%s">'
                  % (self.name, self.name)]

        values = self.__values

        if not self.context.required or selected is None:
            result.append('<option value="%s"></option>' % self._missing)

        for value in values:
            if value == selected:
                result.append("<option selected>%s</option>" % value)
            else:
                result.append("<option>%s</option>" % value)

        result.append('</select>')
        return '\n\t'.join(result)

    def __call__(self):
        if self.__values is not None:
            return self._select()

        displayMaxWidth = self.getValue('displayMaxWidth') or 0
        if displayMaxWidth > 0:
            return renderElement(self.getValue('tag'),
                                 type = self.getValue('type'),
                                 name = self.name,
                                 id = self.name,
                                 value = self._showData(),
                                 cssClass = self.getValue('cssClass'),
                                 style = self.style,
                                 size = self.getValue('displayWidth'),
                                 maxlength = displayMaxWidth,
                                 extra = self.getValue('extra'))
        else:
            return renderElement(self.getValue('tag'),
                                 type = self.getValue('type'),
                                 name = self.name,
                                 id = self.name,
                                 value = self._showData(),
                                 cssClass = self.getValue('cssClass'),
                                 style = self.style,
                                 size = self.getValue('displayWidth'),
                                 extra = self.getValue('extra'))

class Bytes:

    def _convert(self, value):
        if self.context.min_length and not value:
            return None

        value = super(Bytes, self)._convert(value)
        if type(value) is unicode:
            try:
                value = value.encode('ascii')
            except UnicodeError, v:
                raise ConversionError("Invalid textual data", v)

        return value

class BytesWidget(Bytes, TextWidget):
    pass

class IntWidget(TextWidget):
    displayWidth = 10

    def _convert(self, value):
        if value:
            try:
                return int(value)
            except ValueError, v:
                raise ConversionError("Invalid integer data", v)


class FloatWidget(TextWidget):
    displayWidth = 10

    def _convert(self, value):
        if value:
            try:
                return float(value)
            except ValueError, v:
                raise ConversionError("Invalid floating point data", v)

class TextAreaWidget(PossiblyEmptyMeansMissing, BrowserWidget):
    """Textarea widget."""
    propertyNames = BrowserWidget.propertyNames + ['width', 'height', 'extra']

    default = ""
    width = 60
    height = 15
    extra=""
    #style="width:100%"
    style = ''

    def _convert(self, value):
        if self.context.min_length and not value:
            return None
        return value

    def __call__(self):
        return renderElement("textarea",
                             name = self.name,
                             id = self.name,
                             cssClass = self.getValue('cssClass'),
                             rows = self.getValue('height'),
                             cols = self.getValue('width'),
                             style = self.style,
                             contents = self._showData(),
                             extra = self.getValue('extra'))

    def row(self):
        # XXX This was originally set to make a colspan=2 table cell, and
        #     have the label above the text area. Perhaps we should use
        #     different div classes for this case?
        return '<div class="label">%s</div><div class="field">%s</div>' % (
                self.label(), self())

class BytesAreaWidget(Bytes, TextAreaWidget):
    pass

class PasswordWidget(TextWidget):
    """Password Widget"""
    type='password'

    def __call__(self):
        displayMaxWidth = self.getValue('displayMaxWidth') or 0
        if displayMaxWidth > 0:
            return renderElement(self.getValue('tag'),
                                 type = self.getValue('type'),
                                 name = self.name,
                                 id = self.name,
                                 value = '',
                                 cssClass = self.getValue('cssClass'),
                                 style = self.style,
                                 size = self.getValue('displayWidth'),
                                 maxlength = displayMaxWidth,
                                 extra = self.getValue('extra'))
        else:
            return renderElement(self.getValue('tag'),
                                 type = self.getValue('type'),
                                 name = self.name,
                                 id = self.name,
                                 value = '',
                                 cssClass = self.getValue('cssClass'),
                                 style = self.style,
                                 size = self.getValue('displayWidth'),
                                 extra = self.getValue('extra'))

    def hidden(self):
        raise NotImplementedError(
            'Cannot get a hidden tag for a password field')

class FileWidget(TextWidget):
    """File Widget"""
    type = 'file'

    def __call__(self):
        displayMaxWidth = self.getValue('displayMaxWidth') or 0
        if displayMaxWidth > 0:
            return renderElement(self.getValue('tag'),
                                 type = self.getValue('type'),
                                 name = self.name,
                                 id = self.name,
                                 cssClass = self.getValue('cssClass'),
                                 size = self.getValue('displayWidth'),
                                 maxlength = displayMaxWidth,
                                 extra = self.getValue('extra'))
        else:
            return renderElement(self.getValue('tag'),
                                 type = self.getValue('type'),
                                 name = self.name,
                                 id = self.name,
                                 cssClass = self.getValue('cssClass'),
                                 size = self.getValue('displayWidth'),
                                 extra = self.getValue('extra'))

    def haveData(self):
        file = self.request.form.get(self.name)
        if file is None:
            return False

        if getattr(file, 'filename', ''):
            return True

        try:
            seek = file.seek
            read = file.read
        except AttributeError, e:
            return False

        seek(0)
        if read(1):
            return True

        return False

    def _convert(self, value):
        try:
            seek = value.seek
            read = value.read
        except AttributeError, e:
            raise ConversionError('Value is not a file object', e)
        else:
            seek(0)
            data = read()
            if data or getattr(value, 'filename', ''):
                return data
            else:
                return None


class ItemsWidget(BrowserWidget):
    """A widget that has a number of items in it."""

    # What the heck is this for?


class SingleItemsWidget(ItemsWidget):
    """A widget with a number of items that has only a single
    selectable item."""
    default = ""
    firstItem = False

    def textForValue(self, value):
        '''Returns the text for the given value.

        Override this in subclasses.'''
        return value

    def renderItems(self, value):
        name = self.name
        # get items
        items = self.context.allowed_values

        # check if we want to select first item
        if (not value and getattr(self.context, 'firstItem', False)
            and len(items) > 0):
            value = items[0]

        cssClass = self.getValue('cssClass')

        # FIXME: what if we run into multiple items with same value?
        rendered_items = []
        count = 0
        for item_value in items:
            item_text = self.textForValue(item_value)

            if item_value == value:
                rendered_item = self.renderSelectedItem(count,
                                                        item_text,
                                                        item_value,
                                                        name,
                                                        cssClass)
            else:
                rendered_item = self.renderItem(count,
                                                item_text,
                                                item_value,
                                                name,
                                                cssClass)

            rendered_items.append(rendered_item)
            count += 1

        return rendered_items


class ListWidget(SingleItemsWidget):
    """List widget."""
    __implements__ = SingleItemsWidget.__implements__
    propertyNames = (SingleItemsWidget.propertyNames +
                     ['firstItem', 'items', 'size', 'extra']
                     )
    size = 5

    def __call__(self):
        renderedItems = self.renderItems(self._showData())
        return renderElement('select',
                              name = self.name,
                              id = self.name,
                              cssClass = self.getValue('cssClass'),
                              size = self.getValue('size'),
                              contents = "\n".join(renderedItems),
                              extra = self.getValue('extra'))

    def renderItem(self, index, text, value, name, cssClass):
        return renderElement('option', contents=text, value=value,
                              cssClass=cssClass)

    def renderSelectedItem(self, index, text, value, name, cssClass):
        return renderElement('option', contents=text, value=value,
                              cssClass=cssClass, selected=None)


class RadioWidget(SingleItemsWidget):
    """Radio buttons widget."""
    propertyNames = SingleItemsWidget.propertyNames +\
                     ['firstItem', 'orientation']
    orientation = "vertical"

    def __call__(self):
        rendered_items = self.renderItems(self._showData())
        orientation = self.getValue('orientation')
        if orientation == 'horizontal':
            return "&nbsp;&nbsp;".join(rendered_items)
        else:
            return '<br />'.join(rendered_items)

    def _renderItem(self, index, text, value, name, cssClass, checked):
        id = '%s.%s' % (name, index)
        if checked:
            element = renderElement('input',
                                    type="radio",
                                    cssClass=cssClass,
                                    name=name,
                                    id=id,
                                    value=value,
                                    checked=None)
        else:
            element = renderElement('input',
                                    type="radio",
                                    cssClass=cssClass,
                                    name=name,
                                    id=id,
                                    value=value)

        return '%s<label for="%s">%s</label>' % (element, id, text)

    def renderItem(self, index, text, value, name, cssClass):
        return self._renderItem(index, text, value, name, cssClass, False)

    def renderSelectedItem(self, index, text, value, name, cssClass):
        return self._renderItem(index, text, value, name, cssClass, True)

class MultiItemsWidget(ItemsWidget):
    """A widget with a number of items that has multiple selectable items."""
    default = []

    def _convert(self, value, ListTypes = (list, tuple)):
        if value is None:
            return []
        if isinstance(value, ListTypes):
            return value
        return [value]

    def renderItems(self, value):
        # need to deal with single item selects
        value = removeAllProxies(value)

        if not isinstance(value, ListTypes):
            value = [value]
        name = self.name
        items = self.context.allowed_values
        cssClass = self.getValue('cssClass')
        rendered_items = []
        count = 0
        for item in items:
            try:
                item_value, item_text = item
            except ValueError:
                item_value = item
                item_text = item

            if item_value in value:
                rendered_item = self.renderSelectedItem(count,
                                                        item_text,
                                                        item_value,
                                                        name,
                                                        cssClass)
            else:
                rendered_item = self.renderItem(count,
                                                item_text,
                                                item_value,
                                                name,
                                                cssClass)

            rendered_items.append(rendered_item)
            count += 1

        return rendered_items


class MultiListWidget(MultiItemsWidget):
    """List widget with multiple select."""
    propertyNames = MultiItemsWidget.propertyNames + ['size', 'extra']
    size = 5

    def __call__(self):
        rendered_items = self.renderItems(self._showData())
        return renderElement('select',
                              name = self.name,
                              id = self.name,
                              multiple = None,
                              cssClass = self.getValue('cssClass'),
                              size = self.getValue('size'),
                              contents = "\n".join(rendered_items),
                              extra = self.getValue('extra'))

    def renderItem(self, index, text, value, name, cssClass):
        return renderElement('option', contents=text, value=value)

    def renderSelectedItem(self, index, text, value, name, cssClass):
        return renderElement('option', contents=text, value=value,
                              selected=None)


class MultiCheckBoxWidget(MultiItemsWidget):
    """Multiple checkbox widget."""
    propertyNames = MultiItemsWidget.propertyNames + ['orientation']
    orientation = "vertical"

    def __call__(self):
        rendered_items = self.renderItems(self._showData())
        orientation = self.getValue('orientation')
        if orientation == 'horizontal':
            return "&nbsp;&nbsp;".join(rendered_items)
        else:
            return "<br />".join(rendered_items)

    def renderItem(self, index, text, value, name, cssClass):
        return renderElement('input',
                              type = "checkbox",
                              cssClass = cssClass,
                              name = name,
                              id = name,
                              value = value) + text

    def renderSelectedItem(self, index, text, value, name, cssClass):
        return renderElement('input',
                              type = "checkbox",
                              cssClass = cssClass,
                              name = name,
                              id = name,
                              value = value,
                              checked = None) + text


# XXX Note, some HTML quoting is needed in renderTag and renderElement.

def renderTag(tag, **kw):
    """Render the tag. Well, not all of it, as we may want to / it."""
    attr_list = []

    # special case handling for cssClass
    cssClass = ''
    if 'cssClass' in kw:
        if kw['cssClass']:
            cssClass = kw['cssClass']
        del kw['cssClass']

    # If the 'type' attribute is given, append this plus 'Type' as a
    # css class. This allows us to do subselector stuff in css without
    # necessarily having a browser that supports css subselectors.
    # This is important if you want to style radio inputs differently than
    # text inputs.
    cssWidgetType = kw.get('type')
    if cssWidgetType:
        cssWidgetType += 'Type'
    else:
        cssWidgetType = ''
    if cssWidgetType or cssClass:
        attr_list.append('class="%s"' % ' '.join((cssClass, cssWidgetType)))

    if 'style' in kw:
        if kw['style'] != '':
            attr_list.append('style="%s"' % kw['style'])
        del kw['style']

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
