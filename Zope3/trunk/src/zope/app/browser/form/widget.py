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
$Id: widget.py,v 1.36 2003/07/12 01:28:59 richard Exp $
"""

__metaclass__ = type

import re
import warnings
from zope.app import zapi
from zope.interface import implements
from zope.proxy import removeAllProxies
from zope.publisher.browser import BrowserView
from zope.app.interfaces.browser.form import IBrowserWidget
from zope.app.form.widget import Widget
from zope.app.interfaces.form import ConversionError, WidgetInputError
from zope.app.interfaces.form import MissingInputError
from zope.app.datetimeutils import parseDatetimetz
from zope.app.datetimeutils import DateTimeError
from zope.schema.interfaces import ValidationError
from zope.component import getService

ListTypes = list, tuple


class BrowserWidget(Widget, BrowserView):
    """A field widget that knows how to display itself as HTML.

    >>> from zope.publisher.browser import TestRequest
    >>> from zope.schema import Field
    >>> field = Field(__name__='foo', title=u'Foo')
    >>> request = TestRequest(form={'field.foo': u'hello\\r\\nworld'})
    >>> widget = BrowserWidget(field, request)
    >>> widget.name
    'field.foo'
    >>> widget.title
    u'Foo'
    >>> int(widget.haveData())
    1
    >>> widget.getData()
    u'hello\\r\\nworld'
    >>> int(widget.required)
    1
    >>> widget.setData('Hey\\nfolks')
    >>> widget.getData()
    u'hello\\r\\nworld'

    >>> widget.setPrefix('test')
    >>> widget.name
    'test.foo'
    >>> int(widget.haveData())
    0
    >>> widget.getData()
    Traceback (most recent call last):
    ...
    MissingInputError: ('foo', u'Foo', 'the field is required')
    >>> field.required = False
    >>> int(widget.required)
    0
    >>> widget.getData()

    When we generate labels, the labels are translated, so we need to set up
    a lot of machinery to support translation:

    >>> setUp()
    >>> print widget.label()
    <label for="test.foo">Foo</label>
    >>> tearDown()
    
    """

    implements(IBrowserWidget)

    propertyNames = (Widget.propertyNames +
                     ['tag', 'type', 'cssClass', 'extra'])

    tag = 'input'
    type = 'text'
    cssClass = ''
    extra = ''
    _missing = None

    def haveData(self):
        if self.name in self.request.form:
            return self._convert(self.request[self.name]) != self._missing
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
        if self._data is None:
            if self.haveData():
                data = self.getData(1)
            else:
                data = self._getDefault()
        else:
            data = self._data

        return self._unconvert(data)

    def _getDefault(self):
        # Return the default value for this widget;
        # may be overridden by subclasses.
        return self.context.default

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
        warnings.warn("The widget render method is deprecated",
                      DeprecationWarning, 2)

        self.setData(value)
        return self()

    def renderHidden(self, value):
        warnings.warn("The widget render method is deprecated",
                      DeprecationWarning, 2)
        self.setData(value)
        return self.hidden()

    def label(self):
        ts = getService(self.context.context, "Translation")
        title = ts.translate(self.title, "zope", context=self.request)
        if title is None:
            title = self.title
        return '<label for="%s">%s</label>' % (
            self.name,
            title,
            )

    def row(self):
        return '<div class="label">%s</div><div class="field">%s</div>' % (
                self.label(), self())

class DisplayWidget(BrowserWidget):

    def __call__(self):
        return self._showData()

class CheckBoxWidget(BrowserWidget):
    """Checkbox widget

    >>> from zope.publisher.browser import TestRequest
    >>> from zope.schema import Bool
    >>> field = Bool(__name__='foo', title=u'on')
    >>> request = TestRequest(form={'field.foo.used': u'on',
    ...                             'field.foo': u'on'})
    >>> widget = CheckBoxWidget(field, request)
    >>> int(widget.haveData())
    1
    >>> int(widget.getData())
    1
    
    >>> def normalize(s):
    ...   return '\\n  '.join(s.split())

    >>> print normalize( widget() )
    <input
      class="hiddenType"
      id="field.foo.used"
      name="field.foo.used"
      type="hidden"
      value=""
      />
      <input
      class="checkboxType"
      checked="checked"
      id="field.foo"
      name="field.foo"
      type="checkbox"
      />

    >>> print normalize( widget.hidden() )
    <input
      class="hiddenType"
      id="field.foo"
      name="field.foo"
      type="hidden"
      value="on"
      />

    Calling setData will change what gets output:
    
    >>> widget.setData(False)
    >>> print normalize( widget() )
    <input
      class="hiddenType"
      id="field.foo.used"
      name="field.foo.used"
      type="hidden"
      value=""
      />
      <input
      class="checkboxType"
      id="field.foo"
      name="field.foo"
      type="checkbox"
      />

    """
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
        return "%s %s" % (
            renderElement(self.getValue('tag'),
                          type = 'hidden',
                          name = self.name+".used",
                          id = self.name+".used",
                          value=""
                          ),
            renderElement(self.getValue('tag'),
                             type = self.getValue('type'),
                             name = self.name,
                             id = self.name,
                             cssClass = self.getValue('cssClass'),
                             extra = self.getValue('extra'),
                             **kw),
            )

    def _convert(self, value):
        return value == 'on'

    def _unconvert(self, value):
        return value and "on" or ""
        return value == 'on'

    def haveData(self):
        return (
            self.name+".used" in self.request.form
            or
            self.name in self.request.form
            )

    def getData(self, optional=0):
        # When it's checked, its value is 'on'.
        # When a checkbox is unchecked, it does not appear in the form data.
        value = self.request.form.get(self.name, 'off')
        return value == 'on'

class PossiblyEmptyMeansMissing(BrowserWidget):

    def _convert(self, value):
        value = super(PossiblyEmptyMeansMissing, self)._convert(value)
        if not value and getattr(self.context, 'min_length', 1) > 0:
            return None
        return value

class TextWidget(PossiblyEmptyMeansMissing, BrowserWidget):
    """Text widget.

    Single-line text (unicode) input

    >>> from zope.publisher.browser import TestRequest
    >>> from zope.schema import TextLine
    >>> field = TextLine(__name__='foo', title=u'on')
    >>> request = TestRequest(form={'field.foo': u'Bob'})
    >>> widget = TextWidget(field, request)
    >>> int(widget.haveData())
    1
    >>> widget.getData()
    u'Bob'
    
    >>> def normalize(s):
    ...   return '\\n  '.join(filter(None, s.split(' ')))

    >>> print normalize( widget() )
    <input
      class="textType"
      id="field.foo"
      name="field.foo"
      size="20"
      type="text"
      value="Bob"
      />

    >>> print normalize( widget.hidden() )
    <input
      class="hiddenType"
      id="field.foo"
      name="field.foo"
      type="hidden"
      value="Bob"
      />

    Calling setData will change what gets output:
    
    >>> widget.setData("Barry")
    >>> print normalize( widget() )
    <input
      class="textType"
      id="field.foo"
      name="field.foo"
      size="20"
      type="text"
      value="Barry"
      />

    """
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

class Bytes(BrowserWidget):

    def _convert(self, value):
        value = super(Bytes, self)._convert(value)
        if type(value) is unicode:
            try:
                value = value.encode('ascii')
            except UnicodeError, v:
                raise ConversionError("Invalid textual data", v)

        return value

class BytesWidget(Bytes, TextWidget):
    """Bytes widget.

    Single-line data (string) input

    >>> from zope.publisher.browser import TestRequest
    >>> from zope.schema import BytesLine
    >>> field = BytesLine(__name__='foo', title=u'on')
    >>> request = TestRequest(form={'field.foo': u'Bob'})
    >>> widget = BytesWidget(field, request)
    >>> int(widget.haveData())
    1
    >>> widget.getData()
    'Bob'

    """

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

class DatetimeWidget(TextWidget):
    """Datetime entry widget."""
    displayWidth = 20

    def _convert(self, value):
        if value:
            try:
                return parseDatetimetz(value)
            except (DateTimeError, ValueError, IndexError), v:
                raise ConversionError("Invalid datetime data", v)

class TextAreaWidget(PossiblyEmptyMeansMissing, BrowserWidget):
    """TextArea widget.

    Multi-line text (unicode) input.
    
    >>> from zope.publisher.browser import TestRequest
    >>> from zope.schema import Text
    >>> field = Text(__name__='foo', title=u'on')
    >>> request = TestRequest(form={'field.foo': u'Hello\\r\\nworld!'})
    >>> widget = TextAreaWidget(field, request)
    >>> int(widget.haveData())
    1
    >>> widget.getData()
    u'Hello\\nworld!'
    
    >>> def normalize(s):
    ...   return '\\n  '.join(filter(None, s.split(' ')))

    >>> print normalize( widget() )
    <textarea
      cols="60"
      id="field.foo"
      name="field.foo"
      rows="15"
      >Hello\r
    world!</textarea>

    >>> print normalize( widget.hidden() )
    <input
      class="hiddenType"
      id="field.foo"
      name="field.foo"
      type="hidden"
      value="Hello\r
    world!"
      />

    Calling setData will change what gets output:
    
    >>> widget.setData("Hey\\ndude!")
    >>> print normalize( widget() )
    <textarea
      cols="60"
      id="field.foo"
      name="field.foo"
      rows="15"
      >Hey\r
    dude!</textarea>

    """
    propertyNames = BrowserWidget.propertyNames + ['width', 'height', 'extra']

    default = ""
    width = 60
    height = 15
    extra = ""
    style = ''

    def _convert(self, value):
        value = super(TextAreaWidget, self)._convert(value)
        if value:
            value = value.replace("\r\n", "\n")
        return value

    def _unconvert(self, value):
        value = super(TextAreaWidget, self)._unconvert(value)
        if value:
            value = value.replace("\n", "\r\n")
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
    """BytesArea widget.

    Multi-line text (unicode) input.
    
    >>> from zope.publisher.browser import TestRequest
    >>> from zope.schema import Bytes
    >>> field = Bytes(__name__='foo', title=u'on')
    >>> request = TestRequest(form={'field.foo': u'Hello\\r\\nworld!'})
    >>> widget = BytesAreaWidget(field, request)
    >>> int(widget.haveData())
    1
    >>> widget.getData()
    'Hello\\nworld!'

    """

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
        except AttributeError:
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

    def label(self):
        ts = getService(self.context.context, "Translation")
        title = ts.translate(self.title, "zope", context=self.request)
        if title is None:
            title = self.title
        # radio field's label isn't "for" anything
        return title

    def row(self):
        return ('<div class="label"><label for="%s">%s</label></div>'
                '<div class="field" id="%s">%s</div>' % (
                 self.name, self.label(), self.name, self())
                )

class MultiItemsWidget(ItemsWidget):
    """A widget with a number of items that has multiple selectable items."""
    default = []

    def _convert(self, value):
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

class SequenceWidget(BrowserWidget):
    """A sequence of fields.

    Contains a sequence of *Widgets which have a numeric __name__ which
    represents their position in the sequence.
    """
    _type = tuple
    _stored = ()        # pre-existing sequence items (from setData)
    _sequence = ()      # current list of sequence items (existing & request)
    _sequence_generated = False

    def __call__(self):
        """Render the widget
        """
        # XXX we really shouldn't allow value_types of None
        if self.context.value_types is None:
            return ''

        if not self._sequence_generated:
            self._generateSequenceFromRequest()

        render = []
        r = render.append

        # prefix for form elements
        prefix = self._prefix + self.context.__name__

        # length of sequence info
        sequence = list(self._sequence)
        num_items = len(sequence)
        min_length = self.context.min_length
        max_length = self.context.max_length

        # ensure minimum number of items in the form
        if num_items < min_length:
            for i in range(min_length - num_items):
                sequence.append(None)
        num_items = len(sequence)

        # generate each widget from items in the _sequence - adding a
        # "remove" button for each one
        field = self.context.value_types[0]
        for i in range(num_items):
            value = sequence[i]
            r('<tr><td>')
            if num_items > min_length:
                r('<input type="checkbox" name="%s.remove_%d">'%(prefix, i))
            widget = zapi.getView(field, 'edit', self.request, self.context)
            widget.setPrefix('%s.%d.'%(prefix, i))
            widget.setData(value)
            r(widget()+'</td></tr>')
            
        # possibly generate the "remove" and "add" buttons
        s = ''
        if render and num_items > min_length:
            s += '<input type="submit" value="Remove Selected Items">'
        if max_length is None or num_items < max_length:
            s += '<input type="submit" name="%s.add" value="Add %s">'%(prefix,
                field.title or field.__name__)
        if s:
            r('<tr><td>%s</td></tr>'%s)

        return '<table border="0">' + ''.join(render) + '</table>'


    def hidden(self):
        ''' Render the list as hidden fields '''
        prefix = self._prefix + self.context.__name__
        # length of sequence info
        sequence = list(self._sequence)
        num_items = len(sequence)
        min_length = self.context.min_length
        max_length = self.context.max_length

        # ensure minimum number of items in the form
        if num_items < min_length:
            for i in range(min_length - num_items):
                sequence.append(None)
        num_items = len(sequence)

        # generate hidden fields for each value
        field = self.context.value_types[0]
        s = ''
        for i in range(num_items):
            value = sequence[i]
            widget = zapi.getView(field, 'edit', self.request, self.context)
            widget.setPrefix('%s.%d.'%(prefix, i))
            widget.setData(value)
            s += widget.hidden()
        return s

    def getData(self):
        """Return converted and validated widget data.

        If there is no user input and the field is required, then a
        MissingInputError will be raised.

        If there is no user input and the field is not required, then
        the field default value will be returned.

        A WidgetInputError is returned in the case of one or more
        errors encountered, inputting, converting, or validating the data.
        """
        # XXX enforce required
        if not self._sequence_generated:
            self._generateSequenceFromRequest()
        return self._type(self._sequence)

    def haveData(self):
        """Is there input data for the field

        Return True if there is data and False otherwise.
        """
        if not self._sequence_generated:
            self._generateSequenceFromRequest()
        return len(self._sequence) != 0

    def setData(self, value):
        """Set the default data for the widget.

        The given value should be used even if the user has entered
        data.
        """
        # the current list of values derived from the "value" parameter
        self._stored = value
        self._sequence_generated = False

    def _generateSequenceFromRequest(self):
        """Take sequence info in the self.request and populate our _sequence.

        This is kinda expensive, so we only do it once.
        """
        prefix = self._prefix + self.context.__name__
        len_prefix = len(prefix)
        adding = False
        removing = []
        subprefix = re.compile(r'(\d+)\.(.+)')
        if self.context.value_types is None:
            self._sequence = []
            self._sequence_generated = True
            return
        field = self.context.value_types[0]

        # pre-populate 
        found = {}
        for i in range(len(self._stored)):
            entry = self._stored[i]
            found[i] = entry

        # now look through the request for interesting values
        have_request_data = False
        for k, v in self.request.items():
            if not k.startswith(prefix):
                continue
            s = k[len_prefix+1:]        # skip the '.'
            if s == 'add':
                # append a new blank field to the sequence
                adding = True
                have_request_data = True
            elif s.startswith('remove_'):
                # remove the index indicated
                removing.append(int(s[7:]))
                have_request_data = True
            else:
                m = subprefix.match(s)
                if m is None:
                    continue
                # key refers to a sub field
                i = int(m.group(1))
                have_request_data = True

                # find a widget for the sub-field and use that to parse the
                # request data
                widget = zapi.getView(field, 'edit', self.request, self.context)
                widget.setPrefix('%s.%d.'%(prefix, i))
                value = widget.getData()
                field.validate(value)
                found[i] = value

        # remove the indicated indexes 
        for i in  removing:
            del found[i]

        # generate the list, sorting the dict's contents by key
        l = found.items()
        l.sort()
        self._sequence = [v for k,v in l]

        # the submission might add or remove a sequence item
        if adding:
            self._sequence.append(None)

        self._sequence_generated = True

class TupleSequenceWidget(SequenceWidget):
    pass

class ListSequenceWidget(SequenceWidget):
    _type = list


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
        names = filter(None, (cssClass, cssWidgetType))
        attr_list.append('class="%s"' % ' '.join(names))

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
    items = kw.items()
    items.sort()
    for key, value in items:
        if value == None:
            value = key
        attr_list.append('%s="%s"' % (key, str(value)))

    attr_str = " ".join(attr_list)
    return "<%s %s %s" % (tag, attr_str, extra)


def renderElement(tag, **kw):
    if 'contents' in kw:
        contents = kw['contents']
        del kw['contents']
        return "%s>%s</%s>" % (renderTag(tag, **kw), contents, tag)
    else:
        return renderTag(tag, **kw) + " />"

def setUp():
    import zope.app.tests.placelesssetup
    global setUp
    setUp = zope.app.tests.placelesssetup.setUp
    setUp()

def tearDown():
    import zope.app.tests.placelesssetup
    global tearDown
    tearDown = zope.app.tests.placelesssetup.tearDown
    tearDown()
    
