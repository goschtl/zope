##############################################################################
#
# Copyright (c) 2001-2004 Zope Corporation and Contributors.
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
"""Browser Widget Definitions

$Id: widget.py,v 1.1 2004/03/14 01:11:34 srichter Exp $
"""
import re, cgi
import traceback
from warnings import warn
from xml.sax.saxutils import quoteattr

from zope.interface import implements
from zope.proxy import removeAllProxies
from zope.schema import getFieldNamesInOrder
from zope.schema.interfaces import ValidationError
from zope.publisher.browser import BrowserView
from zope.i18n import translate

from zope.app import zapi
from zope.app.tests import ztapi
from zope.app.form.interfaces import IInputWidget
from zope.app.form.browser.interfaces import IBrowserWidget
from zope.app.form.widget import Widget
from zope.app.form.utility import setUpEditWidgets, applyWidgetsChanges
from zope.app.form.interfaces import ConversionError, WidgetInputError
from zope.app.form.interfaces import MissingInputError
from zope.app.datetimeutils import parseDatetimetz
from zope.app.datetimeutils import DateTimeError
from zope.app.i18n import ZopeMessageIDFactory as _

ListTypes = list, tuple

class BrowserWidget(Widget, BrowserView):
    """A field widget that knows how to display itself as HTML.

    When we generate labels, titles, descriptions, and errors, the
    labels, titles, and descriptions are translated and the
    errors are rendered with the view machinery, so we need to set up
    a lot of machinery to support translation and views:
        
    >>> setUp() # now we have to set up an error view...
    >>> from zope.app.form.interfaces import IWidgetInputError
    >>> from zope.app.publisher.browser import BrowserView
    >>> from cgi import escape
    >>> class SnippetErrorView(BrowserView):
    ...     def __call__(self):
    ...         return escape(self.context.errors[0])
    ...
    >>> ztapi.browserView(IWidgetInputError, 'snippet', SnippetErrorView)
    >>> from zope.publisher.browser import TestRequest

    And now the tests proper...

    >>> from zope.schema import Field
    >>> import re
    >>> isFriendly=re.compile(".*hello.*").match
    >>> field = Field(__name__='foo', title=u'Foo', constraint=isFriendly)
    >>> request = TestRequest(form={
    ... 'field.foo': u'hello\\r\\nworld',
    ... 'baz.foo': u'bye world'})
    >>> widget = BrowserWidget(field, request)
    >>> widget.name
    'field.foo'
    >>> widget.title
    u'Foo'
    >>> widget.hasInput()
    True
    >>> widget.getInputValue()
    u'hello\\r\\nworld'
    >>> widget.required
    True
    >>> widget._error is None
    True
    >>> widget.error()
    ''
    >>> widget.setRenderedValue('Hey\\nfolks')
    >>> widget.getInputValue()
    u'hello\\r\\nworld'
    >>> widget._error is None
    True
    >>> widget.error()
    ''

    >>> widget.setPrefix('baz')
    >>> widget.name
    'baz.foo'
    >>> widget.error()
    ''
    >>> try:
    ...     widget.getInputValue()
    ... except WidgetInputError:
    ...     print widget._error.errors
    (u'Constraint not satisfied', u'bye world')
    >>> widget.error()
    u'Constraint not satisfied'
    >>> widget._error = None # clean up for next round of tests

    >>> widget.setPrefix('test')
    >>> widget.name
    'test.foo'
    >>> widget._error is None
    True
    >>> widget.error()
    ''
    >>> widget.hasInput()
    False
    >>> widget.getInputValue()
    Traceback (most recent call last):
    ...
    MissingInputError: ('test.foo', u'Foo', None)
    >>> field.required = False
    >>> widget.request.form['test.foo'] = u''
    >>> widget.required
    False
    >>> widget.getInputValue() == field.missing_value
    True
    >>> widget._error is None
    True
    >>> widget.error()
    ''

    >>> print widget.label()
    <label for="test.foo">Foo</label>

    Now we clean up.

    >>> tearDown()
    """

    implements(IBrowserWidget)

    tag = 'input'
    type = 'text'
    cssClass = ''
    extra = ''
    _missing = ''
    _error = None
    
    required = property(lambda self: self.context.required)

    def hasInput(self):
        """See IWidget.hasInput.

        Returns True if the submitted request form contains a value for
        the widget, otherwise returns False.

        Some browser widgets may need to implement a more sophisticated test
        for input. E.g. checkbox values are not supplied in submitted
        forms when their value is 'off' -- in this case the widget will
        need to add a hidden element to signal its presence in the form.
        """
        return self.name in self.request.form

    def hasValidInput(self):
        try:
            self.getInputValue()
            return True
        except WidgetInputError:
            return False

    def getInputValue(self):
        self._error = None
        field = self.context

        # form input is required, otherwise raise an error
        input = self.request.form.get(self.name)
        if input is None:
            raise MissingInputError(self.name, self.title, None)

        # convert input to suitable value - may raise conversion error
        value = self._convert(input)

        # allow missing values only for non-required fields
        if value == field.missing_value and not field.required:
            return value

        # value must be valid per the field constraints
        try:
            field.validate(value)
        except ValidationError, v:
            self._error = WidgetInputError(
                self.context.__name__, self.title, v)
            raise self._error
        return value

    def validate(self):
        self.getInputValue()

    def applyChanges(self, content):
        field = self.context
        value = self.getInputValue()
        if field.query(content, self) != value:
            field.set(content, value)
            return True
        else:
            return False

    def _convert(self, input):
        """Converts input to a value appropriate for the field type.

        Widgets for non-string fields should override this method to
        perform an appropriate conversion.

        This method is used by getInputValue to perform the conversion
        of a form input value (keyed by the widget's name) to an appropriate
        field value. Widgets that require a more complex conversion process
        (e.g. utilize more than one form field) should override getInputValue
        and disregard this method.
        """
        if input == self._missing:
            return self.context.missing_value
        else:
            return input

    def _unconvert(self, value):
        """Converts a field value to a string used as an HTML form value.

        This method is used in the default rendering of widgets that can
        represent their values in a single HTML form value. Widgets whose
        fields have more complex data structures should disregard this
        method and override the default rendering method (__call__).
        """
        if value == self.context.missing_value:
            return self._missing
        else:
            return value

    def _showData(self):
        """Returns a value suitable for use as an HTML form value."""

        if not self._renderedValueSet():
            if self.hasInput():
                try:
                    value = self.getInputValue()
                except WidgetInputError:
                    return self.request.form.get(self.name, self._missing)
            else:
                value = self._getDefault()
        else:
            value = self._data

        return self._unconvert(value)

    def _getDefault(self):
        # Return the default value for this widget;
        # may be overridden by subclasses.
        return self.context.default

    def __call__(self):
        return renderElement(self.tag,
                             type=self.type,
                             name=self.name,
                             id=self.name,
                             value=self._showData(),
                             cssClass=self.cssClass,
                             extra=self.extra)

    def hidden(self):
        return renderElement(self.tag,
                             type='hidden',
                             name=self.name,
                             id=self.name,
                             value=self._showData(),
                             cssClass=self.cssClass,
                             extra=self.extra)

    def render(self, value):
        warn("The widget render method is deprecated",
            DeprecationWarning, 2)

        self.setRenderedValue(value)
        return self()

    def renderHidden(self, value):
        warn("The widget render method is deprecated",
            DeprecationWarning, 2)
        self.setRenderedValue(value)
        return self.hidden()

    def label(self):
        kw = {"for": self.name,
              "contents": cgi.escape(self.title)}
        if self.context.description:
            kw["title"] = self.context.description
        return renderElement("label", **kw)

    def error(self):
        if self._error:
            return zapi.getView(self._error, 'snippet', self.request)()
        return ""

    def labelClass(self):
        return self.context.required and "label required" or "label"

    def row(self):
        if self._error:
            return '<div class="%s">%s</div><div class="field">%s</div>' \
                '<div class="error">%s</div>' % (self.labelClass(),
                                                 self.label(), self(),
                                                 self.error())
        else:
            return '<div class="%s">%s</div><div class="field">%s</div>' % (
                self.labelClass(), self.label(), self())
                

class DisplayWidget(BrowserWidget):

    def __call__(self):
        return self._showData()
        

class CheckBoxWidget(BrowserWidget):
    """A checkbox widget used to display Bool fields.
    
    For more detailed documentation, including sample code, see
    tests/test_checkboxwidget.py.
    """
    
    implements(IInputWidget)
    
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
            renderElement(self.tag,
                          type='hidden',
                          name=self.name+".used",
                          id=self.name+".used",
                          value=""
                          ),
            renderElement(self.tag,
                             type=self.type,
                             name=self.name,
                             id=self.name,
                             cssClass=self.cssClass,
                             extra=self.extra,
                             **kw),
            )

    def _convert(self, value):
        return value == 'on'

    def _unconvert(self, value):
        return value and "on" or ""
        return value == 'on'

    def hasInput(self):
        return self.name + ".used" in self.request.form or \
            super(CheckBoxWidget, self).hasInput()

    def getInputValue(self):
        # When it's checked, its value is 'on'.
        # When a checkbox is unchecked, it does not appear in the form data.
        value = self.request.form.get(self.name, 'off')
        return value == 'on'


class TextWidget(BrowserWidget):
    """Text widget.

    Single-line text (unicode) input

    >>> from zope.publisher.browser import TestRequest
    >>> from zope.schema import TextLine
    >>> field = TextLine(__name__='foo', title=u'on')
    >>> request = TestRequest(form={'field.foo': u'Bob'})
    >>> widget = TextWidget(field, request)
    >>> widget.hasInput()
    True
    >>> widget.getInputValue()
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

    Calling setRenderedValue will change what gets output:

    >>> widget.setRenderedValue("Barry")
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
    
    implements(IInputWidget)

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

    def __call__(self):
        displayMaxWidth = self.displayMaxWidth or 0
        if displayMaxWidth > 0:
            return renderElement(self.tag,
                                 type=self.type,
                                 name=self.name,
                                 id=self.name,
                                 value=self._showData(),
                                 cssClass=self.cssClass,
                                 style=self.style,
                                 size=self.displayWidth,
                                 maxlength=displayMaxWidth,
                                 extra=self.extra)
        else:
            return renderElement(self.tag,
                                 type=self.type,
                                 name=self.name,
                                 id=self.name,
                                 value=self._showData(),
                                 cssClass=self.cssClass,
                                 style=self.style,
                                 size=self.displayWidth,
                                 extra=self.extra)

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
    >>> widget.hasInput()
    True
    >>> widget.getInputValue()
    'Bob'
    """    

class ASCII(Bytes):
    """ASCII"""
    

class ASCIIWidget(BytesWidget):
    """ASCII widget.

    Single-line data (string) input
    """

class IntWidget(TextWidget):

    displayWidth = 10

    def _convert(self, value):
        if value == self._missing:
            return self.context.missing_value
        else:
            try:
                return int(value)
            except ValueError, v:
                raise ConversionError("Invalid integer data", v)
                

class FloatWidget(TextWidget):
    
    implements(IInputWidget)
    displayWidth = 10

    def _convert(self, value):
        if value == self._missing:
            return self.context.missing_value
        else:
            try:
                return float(value)
            except ValueError, v:
                raise ConversionError("Invalid floating point data", v)
                

class DatetimeWidget(TextWidget):
    """Datetime entry widget."""

    displayWidth = 20

    def _convert(self, value):
        if value == self._missing:
            return self.context.missing_value
        else:
            try:
                return parseDatetimetz(value)
            except (DateTimeError, ValueError, IndexError), v:
                raise ConversionError("Invalid datetime data", v)
                

class DateWidget(TextWidget):
    """Date entry widget.
    """

    displayWidth = 20

    def _convert(self, value):
        if value == self._missing:
            return self.context.missing_value
        else:
            try:
                return parseDatetimetz(value).date()
            except (DateTimeError, ValueError, IndexError), v:
                raise ConversionError("Invalid datetime data", v)
                

class TextAreaWidget(BrowserWidget):
    """TextArea widget.

    Multi-line text (unicode) input.

    >>> from zope.publisher.browser import TestRequest
    >>> from zope.schema import Text
    >>> field = Text(__name__='foo', title=u'on')
    >>> request = TestRequest(form={'field.foo': u'Hello\\r\\nworld!'})
    >>> widget = TextAreaWidget(field, request)
    >>> widget.hasInput()
    True
    >>> widget.getInputValue()
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

    Calling setRenderedValue will change what gets output:

    >>> widget.setRenderedValue("Hey\\ndude!")
    >>> print normalize( widget() )
    <textarea
      cols="60"
      id="field.foo"
      name="field.foo"
      rows="15"
      >Hey\r
    dude!</textarea>

    """

    implements(IInputWidget)

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
                             name=self.name,
                             id=self.name,
                             cssClass=self.cssClass,
                             rows=self.height,
                             cols=self.width,
                             style=self.style,
                             contents=self._showData(),
                             extra=self.extra)

class BytesAreaWidget(Bytes, TextAreaWidget):
    """BytesArea widget.

    Multi-line string input.

    >>> from zope.publisher.browser import TestRequest
    >>> from zope.schema import Bytes
    >>> field = Bytes(__name__='foo', title=u'on')
    >>> request = TestRequest(form={'field.foo': u'Hello\\r\\nworld!'})
    >>> widget = BytesAreaWidget(field, request)
    >>> widget.hasInput()
    True
    >>> widget.getInputValue()
    'Hello\\nworld!'
    """    

class PasswordWidget(TextWidget):
    """Password Widget"""
    
    type = 'password'

    def __call__(self):
        displayMaxWidth = self.displayMaxWidth or 0
        if displayMaxWidth > 0:
            return renderElement(self.tag,
                                 type=self.type,
                                 name=self.name,
                                 id=self.name,
                                 value='',
                                 cssClass=self.cssClass,
                                 style=self.style,
                                 size=self.displayWidth,
                                 maxlength=displayMaxWidth,
                                 extra=self.extra)
        else:
            return renderElement(self.tag,
                                 type=self.type,
                                 name=self.name,
                                 id=self.name,
                                 value='',
                                 cssClass=self.cssClass,
                                 style=self.style,
                                 size=self.displayWidth,
                                 extra=self.extra)

    def hidden(self):
        raise NotImplementedError(
            'Cannot get a hidden tag for a password field')
            

class FileWidget(TextWidget):
    """File Widget"""
    
    type = 'file'

    def __call__(self):
        displayMaxWidth = self.displayMaxWidth or 0
        if displayMaxWidth > 0:
            return renderElement(self.tag,
                                 type=self.type,
                                 name=self.name,
                                 id=self.name,
                                 cssClass=self.cssClass,
                                 size=self.displayWidth,
                                 maxlength=displayMaxWidth,
                                 extra=self.extra)
        else:
            return renderElement(self.tag,
                                 type=self.type,
                                 name=self.name,
                                 id=self.name,
                                 cssClass=self.cssClass,
                                 size=self.displayWidth,
                                 extra=self.extra)

    def hasInput(self):
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
                return self.context.missing_value


class ItemsWidget(BrowserWidget):
    """A widget that has a number of items in it."""
    # What the heck is this for?
    
    implements(IInputWidget)
    

class SingleItemsWidget(ItemsWidget):
    """A widget with a number of items that has only a single
    selectable item."""
    
    default = ""
    firstItem = False

    def textForValue(self, value):
        '''Returns the text for the given value.

        Override this in subclasses.'''
        # The text could be a MessageID, in which case we should try to
        # translate it.
        return translate(self.context, value, context=self.request,
                         default=value)

    def renderItems(self, value):
        name = self.name
        # get items
        items = self.context.allowed_values

        # check if we want to select first item
        if (not value and getattr(self.context, 'firstItem', False)
            and len(items) > 0):
            value = items[0]

        cssClass = self.cssClass

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
    
    size = 5

    def __call__(self):
        renderedItems = self.renderItems(self._showData())
        return renderElement('select',
                              name=self.name,
                              id=self.name,
                              cssClass=self.cssClass,
                              size=self.size,
                              contents="\n".join(renderedItems),
                              extra=self.extra)

    def renderItem(self, index, text, value, name, cssClass):
        return renderElement('option', contents=text, value=value,
                              cssClass=cssClass)

    def renderSelectedItem(self, index, text, value, name, cssClass):
        return renderElement('option', contents=text, value=value,
                              cssClass=cssClass, selected=None)


class RadioWidget(SingleItemsWidget):
    """Radio buttons widget."""
    
    orientation = "vertical"

    def __call__(self):
        rendered_items = self.renderItems(self._showData())
        orientation = self.orientation
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
        return translate(self.context, self.title, context=self.request,
                         default=self.title)

    def row(self):
        return ('<div class="%s"><label for="%s">%s</label></div>'
                '<div class="field" id="%s">%s</div>' % (
                self.labelClass(), self.name, self.label(), self.name, self()))
                

class MultiItemsWidget(ItemsWidget):
    """A widget with a number of items that has multiple selectable items."""
        
    default = []

    def _convert(self, value):
        if not value:
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
        cssClass = self.cssClass
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

    size = 5

    def __call__(self):
        rendered_items = self.renderItems(self._showData())
        return renderElement('select',
                              name=self.name,
                              id=self.name,
                              multiple=None,
                              cssClass=self.cssClass,
                              size=self.size,
                              contents="\n".join(rendered_items),
                              extra=self.extra)

    def renderItem(self, index, text, value, name, cssClass):
        return renderElement('option', contents=text, value=value)

    def renderSelectedItem(self, index, text, value, name, cssClass):
        return renderElement('option', contents=text, value=value,
                              selected=None)


class MultiCheckBoxWidget(MultiItemsWidget):
    """Multiple checkbox widget."""

    orientation = "vertical"

    def __call__(self):
        rendered_items = self.renderItems(self._showData())
        orientation = self.orientation
        if orientation == 'horizontal':
            return "&nbsp;&nbsp;".join(rendered_items)
        else:
            return "<br />".join(rendered_items)

    def renderItem(self, index, text, value, name, cssClass):
        return renderElement('input',
                              type="checkbox",
                              cssClass=cssClass,
                              name=name,
                              id=name,
                              value=value) + text

    def renderSelectedItem(self, index, text, value, name, cssClass):
        return renderElement('input',
                              type="checkbox",
                              cssClass=cssClass,
                              name=name,
                              id=name,
                              value=value,
                              checked=None) + text
                              

class SequenceWidget(BrowserWidget):
    """A widget baseclass for a sequence of fields.

    subwidget  - Optional CustomWidget used to generate widgets for the
                 items in the sequence
    """

    implements(IInputWidget)

    _type = tuple    
    _data = () # pre-existing sequence items (from setRenderedValue)

    def __init__(self, context, request, subwidget=None):
        super(SequenceWidget, self).__init__(context, request)

        self.subwidget = None

    def __call__(self):
        """Render the widget
        """
        # XXX we really shouldn't allow value_type of None
        if self.context.value_type is None:
            return ''

        render = []

        # length of sequence info
        sequence = list(self._generateSequence())
        num_items = len(sequence)
        min_length = self.context.min_length
        max_length = self.context.max_length

        # ensure minimum number of items in the form
        if num_items < min_length:
            for i in range(min_length - num_items):
                sequence.append(None)
        num_items = len(sequence)

        # generate each widget from items in the sequence - adding a
        # "remove" button for each one
        for i in range(num_items):
            value = sequence[i]
            render.append('<tr><td>')
            if num_items > min_length:
                render.append(
                    '<input type="checkbox" name="%s.remove_%d" />' % (
                    self.name, i)
                    )
            widget = self._getWidget(i)
            widget.setRenderedValue(value)
            render.append(widget() + '</td></tr>')

        # possibly generate the "remove" and "add" buttons
        buttons = ''
        if render and num_items > min_length:
            button_label = _('remove-selected-items', "Remove selected items")
            button_label = translate(self.context, button_label,
                                     context=self.request, default=button_label)
            buttons += '<input type="submit" value="%s" />' % button_label
        if max_length is None or num_items < max_length:
            field = self.context.value_type
            button_label = _('Add %s')
            button_label = translate(self.context, button_label,
                                     context=self.request, default=button_label)
            button_label = button_label % (field.title or field.__name__)
            buttons += '<input type="submit" name="%s.add" value="%s" />' % (
                self.name, button_label)
        if buttons:
            render.append('<tr><td>%s</td></tr>' % buttons)

        return '<table border="0">' + ''.join(render) + '</table>'

    def _getWidget(self, i):
        field = self.context.value_type
        if self.subwidget:
            widget = self.subwidget(field, self.request)
        else:
            widget = zapi.getViewProviding(field, IInputWidget, self.request,
                                           context=self.context)
        widget.setPrefix('%s.%d.'%(self.name, i))
        return widget

    def hidden(self):
        ''' Render the list as hidden fields '''
        # length of sequence info
        sequence = self._generateSequence()
        num_items = len(sequence)
        min_length = self.context.min_length

        # ensure minimum number of items in the form
        if num_items < min_length:
            for i in range(min_length - num_items):
                sequence.append(None)
        num_items = len(sequence)

        # generate hidden fields for each value
        s = ''
        for i in range(num_items):
            value = sequence[i]
            widget = self._getWidget(i)
            widget.setRenderedValue(value)
            s += widget.hidden()
        return s

    def getInputValue(self):
        """Return converted and validated widget data.

        If there is no user input and the field is required, then a
        MissingInputError will be raised.

        If there is no user input and the field is not required, then
        the field default value will be returned.

        A WidgetInputError is returned in the case of one or more
        errors encountered, inputting, converting, or validating the data.
        """
        sequence = self._generateSequence()
        # validate the input values
        for value in sequence:
            self.context.value_type.validate(value)
        return self._type(sequence)

    # XXX applyChanges isn't reporting "change" correctly (we're
    # re-generating the sequence with every edit, and need to be smarter)
    def applyChanges(self, content):
        field = self.context
        value = self.getInputValue()
        change = field.query(content, self) != value
        if change:
            field.set(content, value)
        return change

    def hasInput(self):
        """Is there input data for the field

        Return True if there is data and False otherwise.
        """
        return len(self._generateSequence()) != 0

    def setRenderedValue(self, value):
        """Set the default data for the widget.

        The given value should be used even if the user has entered
        data.
        """
        # the current list of values derived from the "value" parameter
        self._data = value

    def _generateSequence(self):
        """Take sequence info in the self.request and _data.
        """
        len_prefix = len(self.name)
        adding = False
        removing = []
        subprefix = re.compile(r'(\d+)\.(.*)$')
        if self.context.value_type is None:
            return []

        # pre-populate
        found = {}
        if self._data is not None:
            found = dict(enumerate(self._data))

        # now look through the request for interesting values
        for key in self.request.keys():
            if not key.startswith(self.name):
                continue
            token = key[len_prefix+1:]        # skip the '.'
            if token == 'add':
                # append a new blank field to the sequence
                adding = True
            elif token.startswith('remove_'):
                # remove the index indicated
                removing.append(int(token[7:]))
            else:
                match = subprefix.match(token)
                if match is None:
                    continue
                # key refers to a sub field
                i = int(match.group(1))

                # find a widget for the sub-field and use that to parse the
                # request data
                widget = self._getWidget(i)
                value = widget.getInputValue()
                found[i] = value

        # remove the indicated indexes
        for i in removing:
            del found[i]

        # generate the list, sorting the dict's contents by key
        items = found.items()
        items.sort()
        sequence = [value for key, value in items]

        # add an entry to the list if the add button has been pressed
        if adding:
            sequence.append(None)

        return sequence


class TupleSequenceWidget(SequenceWidget):
    pass

class ListSequenceWidget(SequenceWidget):
    
    _type = list


class ObjectWidget(BrowserWidget):
    """A widget over an Interface that contains Fields.

    "factory"  - factory used to create content that this widget (field)
                 represents
    *_widget   - Optional CustomWidgets used to generate widgets for the
                 fields in this widget
    """

    implements(IInputWidget)
    
    _object = None      # the object value (from setRenderedValue & request)
    _request_parsed = False

    def __init__(self, context, request, factory, **kw):
        super(ObjectWidget, self).__init__(context, request)

        # factory used to create content that this widget (field)
        # represents
        self.factory = factory

        # handle foo_widget specs being passed in
        self.names = getFieldNamesInOrder(self.context.schema)
        for k, v in kw.items():
            if k.endswith('_widget'):
                setattr(self, k, v)

        # set up my subwidgets
        self._setUpEditWidgets()

    def setPrefix(self, prefix):
        super(ObjectWidget, self).setPrefix(prefix)
        self._setUpEditWidgets()

    def _setUpEditWidgets(self):
        # subwidgets need a new name
        setUpEditWidgets(self, self.context.schema, source=self.context,
                         prefix=self.name, names=self.names, 
                         context=self.context)

    def __call__(self):
        """Render the widget
        """
        render = []

        # XXX see if there's some widget layout already

        # generate each widget from fields in the schema
        field = self.context
        title = field.title or field.__name__
        render.append('<fieldset><legend>%s</legend>'%title)
        for name, widget in self.getSubWidgets():
            render.append(widget.row())
        render.append('</fieldset>')

        return '\n'.join(render)

    def getSubWidgets(self):
        l = []
        for name in self.names:
            l.append((name, getattr(self, '%s_widget'%name)))
        return l

    def hidden(self):
        ''' Render the list as hidden fields '''
        for name, widget in self.getSubWidgets():
            s += widget.hidden()
        return s

    def getInputValue(self):
        """Return converted and validated widget data.

        The value for this field will be represented as an ObjectStorage
        instance which holds the subfield values as attributes. It will
        need to be converted by higher-level code into some more useful
        object (note that the default EditView calls applyChanges, which
        does this).
        """
        content = self.factory()
        for name, widget in self.getSubWidgets():
            setattr(content, name, widget.getInputValue())
        return content

    def applyChanges(self, content):
        field = self.context

        # create our new object value
        value = field.query(content, None)
        if value is None:
            # XXX ObjectCreatedEvent here would be nice
            value = self.factory()

        # apply sub changes, see if there *are* any changes
        # XXX ObjectModifiedEvent here would be nice
        changes = applyWidgetsChanges(self, field.schema, target=value,
                                      names=self.names)

        # if there's changes, then store the new value on the content
        if changes:
            field.set(content, value)

        return changes

    def hasInput(self):
        """Is there input data for the field

        Return True if there is data and False otherwise.
        """
        for name, widget in self.getSubWidgets():
            if widget.hasInput():
                return True
        return False

    def setRenderedValue(self, value):
        """Set the default data for the widget.

        The given value should be used even if the user has entered
        data.
        """
        # re-call setupwidgets with the content
        self._setUpEditWidgets()
        for name, widget in self.getSubWidgets():
            widget.setRenderedValue(getattr(value, name, None))
            

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
            attr_list.append('style=%s' % quoteattr(kw['style']))
        del kw['style']

    # special case handling for extra 'raw' code
    if 'extra' in kw:
        extra = " " + kw['extra'] # could be empty string but we don't care
        del kw['extra']
    else:
        extra = ""

    # handle other attributes
    if kw:
        items = kw.items()
        items.sort()
        for key, value in items:
            if value == None:
                value = key
            attr_list.append('%s=%s' % (key, quoteattr(unicode(value))))

    if attr_list:
        attr_str = " ".join(attr_list)
        return "<%s %s%s" % (tag, attr_str, extra)
    else:
        return "<%s%s" % (tag, extra)


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
