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
$Id: widget.py,v 1.5 2002/12/31 11:07:09 stevea Exp $
"""

__metaclass__ = type

import sys
from types import ListType, TupleType
ListTypes = (ListType, TupleType)
from zope.proxy.introspection import removeAllProxies
from zope.publisher.browser import BrowserView
from zope.app.interfaces.browser.form import IBrowserWidget
from zope.app.form.widget import Widget
from zope.app.interfaces.forms import ConversionError, WidgetInputError
from zope.app.interfaces.forms import MissingInputError
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
        if (self.name) in self.request.form:
            return self._convert(self.request[self.name]) is not None
        return False

    def getData(self, optional=0):
        field = self.context
        value = self.request.form.get(self.name,
                                      self)
        if value is self:
            # No user input
            if field.required and not optional:
                raise MissingInputError(field.__name__, field.title,
                                        'the field is required')
            return field.default

        try:
            value = self._convert(value)
        except ConversionError:
            # Already have right error type
            raise
        except:
            # Convert to conversion error
            exc = ConversionError(sys.exc_info()[1])
            raise ConversionError, exc, sys.exc_info()[2]

        if value is not None or not optional:

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
                             value = self._showData(),
                             cssClass = self.getValue('cssClass'),
                             extra = self.getValue('extra'))

    def hidden(self):
        return renderElement(self.getValue('tag'),
                             type = 'hidden',
                             name = self.name,
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
        return "<td>%s</td><td>%s</td>" % (self.label(), self())

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
            return renderElement(self.getValue('tag'),
                                 type = self.getValue('type'),
                                 name = self.name,
                                 checked = None,
                                 cssClass = self.getValue('cssClass'),
                                 extra = self.getValue('extra'))
        else:
            return renderElement(self.getValue('tag'),
                                 type = self.getValue('type'),
                                 name = self.name,
                                 cssClass = self.getValue('cssClass'),
                                 size = self.getValue('displayWidth'),
                                 extra = self.getValue('extra'))

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
            return 0
        if not v and self.context.min_length > 0:
            return 0
        return 1

    def _convert(self, value):
        v = self.request.form.get(self.name)
        if not v and self.context.min_length > 0:
            return None
        return v

class TextWidget(PossiblyEmptyMeansMissing, BrowserWidget):
    """Text widget."""
    propertyNames = BrowserWidget.propertyNames + \
                     ['displayWidth', 'displayMaxWidth', 'extra', 'default']
    default = ''
    displayWidth = 20
    displayMaxWidth = ""
    extra = ''
    style = "width:100%"
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
        result = ['<select name="%s">'
                  % (self.name)]

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
            value = value.encode('ascii')

        return value

class BytesWidget(Bytes, TextWidget):
    pass

class IntWidget(TextWidget):
    displayWidth = 10

    _convert = int

class FloatWidget(TextWidget):
    displayWidth = 10

    _convert = float

class TextAreaWidget(PossiblyEmptyMeansMissing, BrowserWidget):
    """Textarea widget."""
    propertyNames = BrowserWidget.propertyNames +\
                     ['width', 'height', 'extra']

    default = ""
    width = 60
    height = 15
    extra=""
    style="width:100%"

    def _convert(self, value):
        if self.context.min_length and not value:
            return None
        return value

    def __call__(self):
        return renderElement("textarea",
                             name = self.name,
                             cssClass = self.getValue('cssClass'),
                             rows = self.getValue('height'),
                             cols = self.getValue('width'),
                             style = self.style,
                             contents = self._showData(),
                             extra = self.getValue('extra'))

    def row(self):
        return '<td colspan="2">%s<br />%s</td>' % (self.label(), self())

class BytesAreaWidget(Bytes, TextAreaWidget):
    pass

class PasswordWidget(TextWidget):
    """Password Widget"""
    type='password'


class FileWidget(TextWidget):
    """File Widget"""
    type = 'file'

    def __call__(self):
        displayMaxWidth = self.getValue('displayMaxWidth') or 0
        if displayMaxWidth > 0:
            return renderElement(self.getValue('tag'),
                                 type = self.getValue('type'),
                                 name = self.name,
                                 cssClass = self.getValue('cssClass'),
                                 size = self.getValue('displayWidth'),
                                 maxlength = displayMaxWidth,
                                 extra = self.getValue('extra'))
        else:
            return renderElement(self.getValue('tag'),
                                 type = self.getValue('type'),
                                 name = self.name,
                                 cssClass = self.getValue('cssClass'),
                                 size = self.getValue('displayWidth'),
                                 extra = self.getValue('extra'))

    def haveData(self):
        file = self.request.form.get(self.name)
        if file is None:
            return 0
        if getattr(file, 'filename', ''):
            return 1

        file.seek(0)
        if file.read(1):
            return 1
        return 0

    def _convert(self, value):
        try:
            value.seek(0)
            data = value.read()
        except Exception, e:
            raise ConversionError('Value is not a file object', e)
        else:
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
    firstItem = 0

    def renderItems(self, value):
        name = self.name
        # get items
        items = self.context.allowed_values

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
        renderedItems = self.renderItems(self._showData())
        return renderElement('select',
                              name = self.name,
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
                     ['firstItem', 'orientation']
    orientation = "vertical"

    def __call__(self):
        rendered_items = self.renderItems(self._showData())
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
                     ['size', 'extra']
    size = 5

    def __call__(self):
        rendered_items = self.renderItems(self._showData())
        return renderElement('select',
                              name = self.name,
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
                     ['orientation']
    orientation = "vertical"

    def __call__(self):
        rendered_items = self.renderItems(self._showData())
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
