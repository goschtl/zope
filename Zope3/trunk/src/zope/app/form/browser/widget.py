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

$Id: widget.py,v 1.3 2004/03/18 17:01:10 philikon Exp $
"""
import re, cgi
import traceback
from warnings import warn
from xml.sax.saxutils import quoteattr

from zope.interface import implements
from zope.schema.interfaces import ValidationError
from zope.publisher.browser import BrowserView

from zope.app import zapi
from zope.app.tests import ztapi
from zope.app.form import Widget
from zope.app.form.interfaces import WidgetInputError, MissingInputError
from zope.app.form.browser.interfaces import IBrowserWidget

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
