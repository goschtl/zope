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
$Id$
"""
import unittest, doctest

from zope.app.form.interfaces import IInputWidget
from zope.app.form.browser import CheckBoxWidget
from zope.publisher.browser import TestRequest
from zope.schema import Bool
from zope.interface.verify import verifyClass

from zope.app.form.browser.tests.test_browserwidget import SimpleInputWidgetTest


class CheckBoxWidgetTest(SimpleInputWidgetTest):
    """Documents and tests thec checkbox widget.
        
        >>> verifyClass(IInputWidget, CheckBoxWidget)
        True
        
    The rest of the this doctest was moved from widget.py to this test module
    to keep widget.py free of detailed tests. XXX the tests below should be
    more narrative to highlight the 'story' being told.

    >>> field = Bool(__name__='foo', title=u'on')
    >>> request = TestRequest(form={'field.foo.used': u'on',
    ...                             'field.foo': u'on'})
    >>> widget = CheckBoxWidget(field, request)
    >>> widget.hasInput()
    True
    >>> widget.getInputValue()
    True

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

    Calling setRenderedValue will change what gets output:

    >>> widget.setRenderedValue(False)
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

    When a checkbox is not 'checked', it's value is not
    sent in the request, so we consider it 'False', which
    means that 'required' for a boolean field doesn't make
    much sense in the end.

    >>> field = Bool(__name__='foo', title=u'on', required=True)
    >>> request = TestRequest(form={'field.foo.used': u''})
    >>> widget = CheckBoxWidget(field, request)
    >>> widget.hasInput()
    True
    >>> widget.validate()
    >>> widget.getInputValue()
    False
    """

    _FieldFactory = Bool
    _WidgetFactory = CheckBoxWidget

    def testProperties(self):
        self.assertEqual(self._widget.tag, 'input')
        self.assertEqual(self._widget.type, 'checkbox')
        self.assertEqual(self._widget.cssClass, '')
        self.assertEqual(self._widget.extra, '')
        self.assertEqual(self._widget.default, 0)

    def testRender(self):
        value = 1
        self._widget.setRenderedValue(value)
        check_list = ('type="checkbox"', 'id="field.foo"',
                      'name="field.foo"', 'checked="checked"')
        self.verifyResult(self._widget(), check_list)
        value = 0
        self._widget.setRenderedValue(value)
        check_list = check_list[:-1]
        self.verifyResult(self._widget(), check_list)
        check_list = ('type="hidden"',) + check_list[1:-1]
        self.verifyResult(self._widget.hidden(), check_list)
        check_list = ('style="color: red"',) + check_list
        self._widget.extra = 'style="color: red"'
        self.verifyResult(self._widget.hidden(), check_list)

    def test_getInputValue(self):
        self._widget.request.form['field.foo'] = 'on'
        self.assertEqual(self._widget.getInputValue(), True)
        self._widget.request.form['field.foo'] = 'positive'
        self.assertEqual(self._widget.getInputValue(), False)
        del self._widget.request.form['field.foo']
        self.assertEqual(self._widget.getInputValue(), False)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(CheckBoxWidgetTest),
        doctest.DocTestSuite(),
        ))

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
