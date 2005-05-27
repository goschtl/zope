##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Text Widget tests

$Id$
"""
import unittest, doctest

from zope.interface.verify import verifyClass
from zope.schema import TextLine
from zope.publisher.browser import TestRequest

from zope.app.form.interfaces import IInputWidget
from zope.app.form.browser import TextWidget
from zope.app.tests.placelesssetup import setUp, tearDown
from zope.app.form.browser.tests.test_browserwidget import SimpleInputWidgetTest


class TextWidgetTest(SimpleInputWidgetTest):
    """Documents and tests the text widget.
    >>> setUp()

        >>> verifyClass(IInputWidget, TextWidget)
        True

    Converting Missing Values
    -------------------------
    String fields (TextLine, Text, etc.) values can be classified as one of the
    following:

      - Non-empty string
      - Empty string
      - None

    Text browser widgets only support the first two types: non-empty strings
    and empty strings. There's no facility to explicitly set a None value in a
    text browser widget.

    However, it is possible to interpret an empty string as None for some
    applications. For example, when inputing a User Name, an empty string means
    'the user hasn't provided a value'. In another application, an empty string
    may mean 'the user has provided a value, specifically <empty string>'.

    To support both modes, the text widget provides a 'convert_missing_value'
    flag. When True, empty strings will be converted by the widget to the
    field's 'missing_value' (None by default). This mode accommodates the
    'user hasn't provided a value' scenario.

    To illustrate this mode, we'll use an optional field, where missing_value
    is None:

        >>> field = TextLine(
        ...     __name__='foo',
        ...     missing_value=None,
        ...     required=False)

    The HTTP form submission contains an empty string for the field value:

        >>> request = TestRequest(form={'field.foo':u''})

    A text widget configured for the field, where convert_missing_value is True
    (the default value)...

        >>> widget = TextWidget(field, request)
        >>> widget.convert_missing_value
        True

    will convert the form's empty string into the field's missing_value, which
    is None:

        >>> widget.getInputValue() is None
        True

    When 'convert_missing_value' is False, the text widget will not convert
    an empty string to the field's missing_value. This supports the 'user has
    provided a value, specifically <empty string>' mode:

        >>> widget.convert_missing_value = False
        >>> widget.getInputValue()
        u''

    >>> tearDown()
    """

    _WidgetFactory = TextWidget

    def testProperties(self):
        self.assertEqual(self._widget.tag, 'input')
        self.assertEqual(self._widget.type, 'text')
        self.assertEqual(self._widget.cssClass, '')
        self.assertEqual(self._widget.extra, '')
        self.assertEqual(self._widget.default, '')
        self.assertEqual(self._widget.displayWidth, 20)
        self.assertEqual(self._widget.displayMaxWidth, '')

    def testRender(self):
        value = 'Foo Value'
        self._widget.setRenderedValue(value)
        check_list = ('type="text"', 'id="field.foo"', 'name="field.foo"',
                      'value="Foo Value"', 'size="20"')
        self.verifyResult(self._widget(), check_list)
        check_list = ('type="hidden"',) + check_list[1:-1]
        self.verifyResult(self._widget.hidden(), check_list)
        check_list = ('style="color: red"',) + check_list
        self._widget.extra = 'style="color: red"'
        self.verifyResult(self._widget.hidden(), check_list)

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TextWidgetTest),
        doctest.DocTestSuite(),
        ))

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
