##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Browser widgets with text-based input

$Id$
"""
__docformat__ = 'restructuredtext'

from xml.sax import saxutils
from zope.interface import implements

from zope.app.form.interfaces import IInputWidget, ConversionError
from zope.app.form.browser.interfaces import ITextBrowserWidget
from zope.app.form.browser.widget import SimpleInputWidget, renderElement
from zope.app.datetimeutils import parseDatetimetz
from zope.app.datetimeutils import DateTimeError


def escape(str):
    if str is not None:
        str = saxutils.escape(str)
    return str

def unescape(str):
    if str is not None:
        str = saxutils.unescape(str)
    return str


class TextWidget(SimpleInputWidget):
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

    Calling `setRenderedValue` will change what gets output:

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

    Check that HTML is correctly encoded and decoded:

    >>> request = TestRequest(
    ...     form={'field.foo': u'&lt;h1&gt;&amp;copy;&lt;/h1&gt;'})
    >>> widget = TextWidget(field, request)
    >>> widget.getInputValue()
    u'<h1>&copy;</h1>'

    >>> print normalize( widget() )
    <input
      class="textType"
      id="field.foo"
      name="field.foo"
      size="20"
      type="text"
      value="&lt;h1&gt;&amp;copy;&lt;/h1&gt;"
      />
    """

    implements(ITextBrowserWidget)

    default = ''
    displayWidth = 20
    displayMaxWidth = ""
    extra = ''
    style = ''
    convert_missing_value = True

    def __init__(self, *args):
        super(TextWidget, self).__init__(*args)

    def __call__(self):
        displayMaxWidth = self.displayMaxWidth or 0
        if displayMaxWidth > 0:
            return renderElement(self.tag,
                                 type=self.type,
                                 name=self.name,
                                 id=self.name,
                                 value=self._getFormValue(),
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
                                 value=self._getFormValue(),
                                 cssClass=self.cssClass,
                                 style=self.style,
                                 size=self.displayWidth,
                                 extra=self.extra)

    def _toFieldValue(self, input):
        if self.convert_missing_value and input == self._missing:
            value = self.context.missing_value
        else:
            # We convert everything to unicode. This might seem a bit crude,
            # but anything contained in a TextWidget should be representable
            # as a string. Note that you always have the choice of overriding
            # the method.  
            try:
                value = unicode(input)
            except ValueError, v:
                raise ConversionError("Invalid text data", v)
        return unescape(value)


class Bytes(SimpleInputWidget):

    def _toFieldValue(self, input):
        value = super(Bytes, self)._toFieldValue(input)
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

class TextAreaWidget(SimpleInputWidget):
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

    Calling `setRenderedValue` will change what gets output:

    >>> widget.setRenderedValue("Hey\\ndude!")
    >>> print normalize( widget() )
    <textarea
      cols="60"
      id="field.foo"
      name="field.foo"
      rows="15"
      >Hey\r
    dude!</textarea>

    Check that HTML is correctly encoded and decoded:

    >>> request = TestRequest(
    ...     form={'field.foo': u'&lt;h1&gt;&amp;copy;&lt;/h1&gt;'})
    >>> widget = TextAreaWidget(field, request)
    >>> widget.getInputValue()
    u'<h1>&copy;</h1>'

    >>> print normalize( widget() )
    <textarea
      cols="60"
      id="field.foo"
      name="field.foo"
      rows="15"
      >&lt;h1&gt;&amp;copy;&lt;/h1&gt;</textarea>
    """

    default = ""
    width = 60
    height = 15
    extra = ""
    style = ''

    def _toFieldValue(self, value):
        value = super(TextAreaWidget, self)._toFieldValue(value)
        if value:
            try:
                value = unicode(value)
            except ValueError, v:
                raise ConversionError("Invalid unicode data", v)
            else:
                value = unescape(value)
                value = value.replace("\r\n", "\n")                
        return value

    def _toFormValue(self, value):
        value = super(TextAreaWidget, self)._toFormValue(value)
        if value:
            value = value.replace("\n", "\r\n")
            value = escape(value)
        return value

    def __call__(self):
        return renderElement("textarea",
                             name=self.name,
                             id=self.name,
                             cssClass=self.cssClass,
                             rows=self.height,
                             cols=self.width,
                             style=self.style,
                             contents=self._getFormValue(),
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

    def _toFieldValue(self, input):
        if input == '':
            return self.context.missing_value
        try:
            seek = input.seek
            read = input.read
        except AttributeError, e:
            raise ConversionError('Form input is not a file object', e)
        else:
            seek(0)
            data = read()
            if data or getattr(input, 'filename', ''):
                return data
            else:
                return self.context.missing_value

class IntWidget(TextWidget):
    displayWidth = 10

    def _toFieldValue(self, input):
        if input == self._missing:
            return self.context.missing_value
        else:
            try:
                return int(input)
            except ValueError, v:
                raise ConversionError("Invalid integer data", v)


class FloatWidget(TextWidget):
    implements(IInputWidget)
    displayWidth = 10

    def _toFieldValue(self, input):
        if input == self._missing:
            return self.context.missing_value
        else:
            try:
                return float(input)
            except ValueError, v:
                raise ConversionError("Invalid floating point data", v)


class DatetimeWidget(TextWidget):
    """Datetime entry widget."""

    displayWidth = 20

    def _toFieldValue(self, input):
        if input == self._missing:
            return self.context.missing_value
        else:
            try:
                return parseDatetimetz(input)
            except (DateTimeError, ValueError, IndexError), v:
                raise ConversionError("Invalid datetime data", v)


class DateWidget(TextWidget):
    """Date entry widget.
    """

    displayWidth = 20

    def _toFieldValue(self, input):
        if input == self._missing:
            return self.context.missing_value
        else:
            try:
                return parseDatetimetz(input).date()
            except (DateTimeError, ValueError, IndexError), v:
                raise ConversionError("Invalid datetime data", v)
