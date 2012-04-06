##############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
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
"""ExceptionFormatter tests.
"""
import unittest


class TextExceptionFormatterTests(unittest.TestCase):

    def _getTargetClass(self):
        from zope.exceptions.exceptionformatter import TextExceptionFormatter
        return TextExceptionFormatter

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_ctor_defaults(self):
        fmt = self._makeOne()
        self.assertEqual(fmt.line_sep, '\n')
        self.assertEqual(fmt.limit, None)
        self.assertEqual(fmt.with_filenames, False)

    def test_ctor_explicit(self):
        fmt = self._makeOne(limit=20, with_filenames=True)
        self.assertEqual(fmt.line_sep, '\n')
        self.assertEqual(fmt.limit, 20)
        self.assertEqual(fmt.with_filenames, True)

    def test_escape(self):
        fmt = self._makeOne()
        self.assertEqual(fmt.escape('XXX'), 'XXX')

    def test_getPrefix(self):
        fmt = self._makeOne()
        self.assertEqual(fmt.getPrefix(),
                         'Traceback (most recent call last):')

    def test_getLimit_default(self):
        fmt = self._makeOne()
        self.assertEqual(fmt.getLimit(), 200)

    def test_getLimit_sys_has_limit(self):
        import sys
        fmt = self._makeOne()
        with _Monkey(sys, tracebacklimit=15):
            self.assertEqual(fmt.getLimit(), 15)

    def test_getLimit_explicit(self):
        fmt = self._makeOne(limit=10)
        self.assertEqual(fmt.getLimit(), 10)

    def test_formatSupplementLine(self):
        fmt = self._makeOne()
        self.assertEqual(fmt.formatSupplementLine('XXX'), '   - XXX')

    def test_formatSourceURL(self):
        fmt = self._makeOne()
        self.assertEqual(fmt.formatSourceURL('http://example.com/'),
                         ['   - http://example.com/'])

    def test_formatSupplement_no_info(self):
        fmt = self._makeOne()
        supplement = DummySupplement()
        self.assertEqual(fmt.formatSupplement(supplement, tb=None), [])

    def test_formatSupplement_w_source_url(self):
        fmt = self._makeOne()
        supplement = DummySupplement()
        supplement.source_url = 'http://example.com/'
        self.assertEqual(fmt.formatSupplement(supplement, tb=None),
                         ['   - http://example.com/'])

    def test_formatSupplement_w_line_as_marker(self):
        fmt = self._makeOne()
        supplement = DummySupplement()
        supplement.line = -1
        tb = DummyTB()
        self.assertEqual(fmt.formatSupplement(supplement, tb=tb),
                         ['   - Line 14'])

    def test_formatSupplement_w_line_no_column(self):
        fmt = self._makeOne()
        supplement = DummySupplement()
        supplement.line = 23
        self.assertEqual(fmt.formatSupplement(supplement, tb=None),
                         ['   - Line 23'])

    def test_formatSupplement_w_column_no_line(self):
        fmt = self._makeOne()
        supplement = DummySupplement()
        supplement.column = 47
        self.assertEqual(fmt.formatSupplement(supplement, tb=None),
                         ['   - Column 47'])

    def test_formatSupplement_w_line_and_column(self):
        fmt = self._makeOne()
        supplement = DummySupplement()
        supplement.line = 23
        supplement.column = 47
        self.assertEqual(fmt.formatSupplement(supplement, tb=None),
                         ['   - Line 23, Column 47'])

    def test_formatSupplement_w_expression(self):
        fmt = self._makeOne()
        supplement = DummySupplement()
        supplement.expression = 'a*x^2 + b*x + c'
        self.assertEqual(fmt.formatSupplement(supplement, tb=None),
                         ['   - Expression: a*x^2 + b*x + c'])

    def test_formatSupplement_w_warnings(self):
        fmt = self._makeOne()
        supplement = DummySupplement()
        supplement.warnings = ['Beware the ides of March!',
                               'You\'re gonna get wasted.',
                              ]
        self.assertEqual(fmt.formatSupplement(supplement, tb=None),
                         ['   - Warning: Beware the ides of March!',
                          '   - Warning: You\'re gonna get wasted.',
                         ])

    def test_formatSupplement_w_getInfo_empty(self):
        fmt = self._makeOne()
        supplement = DummySupplement()
        supplement.getInfo = lambda *args: ''
        self.assertEqual(fmt.formatSupplement(supplement, tb=None), [])

    def test_formatSupplement_w_getInfo_text(self):
        INFO = 'Some days\nI wish I had stayed in bed.'
        fmt = self._makeOne()
        supplement = DummySupplement()
        supplement.getInfo = lambda *args: INFO
        self.assertEqual(fmt.formatSupplement(supplement, tb=None), [INFO])

    def test_formatTracebackInfo(self):
        fmt = self._makeOne()
        self.assertEqual(fmt.formatTracebackInfo('XYZZY'),
                         '   - __traceback_info__: XYZZY')

    def test_formatLine_no_tb_no_f(self):
        fmt = self._makeOne()
        self.assertRaises(ValueError, fmt.formatLine, None, None)


class Test_format_exception(unittest.TestCase):

    def _callFUT(self, as_html=False):
        import sys
        from zope.exceptions.exceptionformatter import format_exception
        t, v, b = sys.exc_info()
        try:
            return ''.join(format_exception(t, v, b, as_html=as_html))
        finally:
            del b

    def test_basic_names_text(self):
        try:
            raise ExceptionForTesting
        except ExceptionForTesting:
            s = self._callFUT(False)
        # The traceback should include the name of this function.
        self.assertTrue(s.find('test_basic_names_text') >= 0)
        # The traceback should include the name of the exception.
        self.assertTrue(s.find('ExceptionForTesting') >= 0)

    def test_basic_names_html(self):
        try:
            raise ExceptionForTesting
        except ExceptionForTesting:
            s = self._callFUT(True)
        # The traceback should include the name of this function.
        self.assertTrue(s.find('test_basic_names_html') >= 0)
        # The traceback should include the name of the exception.
        self.assertTrue(s.find('ExceptionForTesting') >= 0)

    def test_traceback_info_text(self):
        try:
            __traceback_info__ = "Adam & Eve"
            raise ExceptionForTesting
        except ExceptionForTesting:
            s = self._callFUT(False)
        self.assertTrue(s.find('Adam & Eve') >= 0, s)

    def test_traceback_info_html(self):
        try:
            __traceback_info__ = "Adam & Eve"
            raise ExceptionForTesting
        except ExceptionForTesting:
            s = self._callFUT(True)
        # Be sure quoting is happening.
        self.assertTrue(s.find('Adam &amp; Eve') >= 0, s)

    def test_traceback_info_is_tuple(self):
        try:
            __traceback_info__ = ("Adam", "Eve")
            raise ExceptionForTesting
        except ExceptionForTesting:
            s = self._callFUT(False)
        self.assertTrue(s.find('Adam') >= 0, s)
        self.assertTrue(s.find('Eve') >= 0, s)

    def test_supplement_text(self, as_html=0):
        try:
            __traceback_supplement__ = (TestingTracebackSupplement,
                                        "You're one in a million")
            raise ExceptionForTesting
        except ExceptionForTesting:
            s = self._callFUT(as_html)
        # The source URL
        self.assertTrue(s.find('/somepath') >= 0, s)
        # The line number
        self.assertTrue(s.find('634') >= 0, s)
        # The column number
        self.assertTrue(s.find('57') >= 0, s)
        # The expression
        self.assertTrue(s.find("You're one in a million") >= 0, s)
        # The warning
        self.assertTrue(s.find("Repent, for the end is nigh") >= 0, s)

    def test_supplement_html(self):
        try:
            __traceback_supplement__ = (TestingTracebackSupplement,
                                        "You're one in a million")
            raise ExceptionForTesting
        except ExceptionForTesting:
            s = self._callFUT(True)
        # The source URL
        self.assertTrue(s.find('/somepath') >= 0, s)
        # The line number
        self.assertTrue(s.find('634') >= 0, s)
        # The column number
        self.assertTrue(s.find('57') >= 0, s)
        # The expression
        self.assertTrue(s.find("You're one in a million") >= 0, s)
        # The warning
        self.assertTrue(s.find("Repent, for the end is nigh") >= 0, s)

    def test_multiple_levels(self):
        # Ensure many levels are shown in a traceback.
        HOW_MANY = 10
        def f(n):
            """Produces a (n + 1)-level traceback."""
            __traceback_info__ = 'level%d' % n
            if n > 0:
                f(n - 1)
            else:
                raise ExceptionForTesting
        try:
            f(HOW_MANY)
        except ExceptionForTesting:
            s = self._callFUT(False)
        for n in range(HOW_MANY+1):
            self.assertTrue(s.find('level%d' % n) >= 0, s)

    def test_quote_last_line(self):
        class C(object):
            pass
        try:
            raise TypeError(C())
        except:
            s = self._callFUT(True)
        self.assertTrue(s.find('&lt;') >= 0, s)
        self.assertTrue(s.find('&gt;') >= 0, s)

    def test_multiline_exception(self):
        try:
            exec 'syntax error\n'
        except Exception:
            s = self._callFUT(False)
        self.assertEqual(s.splitlines()[-3:],
                         ['    syntax error',
                          '               ^',
                          'SyntaxError: invalid syntax'])

    def test_recursion_failure(self):
        import sys
        from zope.exceptions.exceptionformatter import TextExceptionFormatter

        class FormatterException(Exception):
            pass

        class FailingFormatter(TextExceptionFormatter):
            def formatLine(self, tb=None, f=None):
                raise FormatterException("Formatter failed")

        fmt = FailingFormatter()
        try:
            raise ExceptionForTesting
        except ExceptionForTesting:
            try:
                fmt.formatException(*sys.exc_info())
            except FormatterException:
                s = self._callFUT(False)
        # Recursion was detected
        self.assertTrue('(Recursive formatException() stopped, '
                        'trying traceback.format_tb)' in s, s)
        # and we fellback to the stdlib rather than hid the real error
        self.assertEqual(s.splitlines()[-2],
                         '    raise FormatterException("Formatter failed")')
        self.assertTrue('FormatterException: Formatter failed'
                        in s.splitlines()[-1])


class Test_extract_stack(unittest.TestCase):

    def _callFUT(self, as_html=False):
        import sys
        from zope.exceptions.exceptionformatter import extract_stack
        f = sys.exc_info()[2].tb_frame
        try:
            return ''.join(extract_stack(f, as_html=as_html))
        finally:
            del f

    def test_basic_names_as_text(self, as_html=0):
        try:
            raise ExceptionForTesting
        except ExceptionForTesting:
            s = self._callFUT(False)
        # The stack trace should include the name of this function.
        self.assertTrue(s.find('test_basic_names_as_text') >= 0)

    def test_basic_names_as_html(self):
        try:
            raise ExceptionForTesting
        except ExceptionForTesting:
            s = self._callFUT(True)
        # The stack trace should include the name of this function.
        self.assertTrue(s.find('test_basic_names_as_html') >= 0)

    def test_traceback_info_text(self):
        try:
            __traceback_info__ = "Adam & Eve"
            raise ExceptionForTesting
        except ExceptionForTesting:
            s = self._callFUT(False)
        self.assertTrue(s.find('Adam & Eve') >= 0, s)

    def test_traceback_info_html(self):
        try:
            __traceback_info__ = "Adam & Eve"
            raise ExceptionForTesting
        except ExceptionForTesting:
            s = self._callFUT(True)
        self.assertTrue(s.find('Adam &amp; Eve') >= 0, s)

    def test_traceback_supplement_text(self):
        try:
            __traceback_supplement__ = (TestingTracebackSupplement,
                                        "You're one in a million")
            raise ExceptionForTesting
        except ExceptionForTesting:
            s = self._callFUT(False)
        # The source URL
        self.assertTrue(s.find('/somepath') >= 0, s)
        # The line number
        self.assertTrue(s.find('634') >= 0, s)
        # The column number
        self.assertTrue(s.find('57') >= 0, s)
        # The expression
        self.assertTrue(s.find("You're one in a million") >= 0, s)
        # The warning
        self.assertTrue(s.find("Repent, for the end is nigh") >= 0, s)

    def test_traceback_supplement_html(self):
        try:
            __traceback_supplement__ = (TestingTracebackSupplement,
                                        "You're one in a million")
            raise ExceptionForTesting
        except ExceptionForTesting:
            s = self._callFUT(True)
        # The source URL
        self.assertTrue(s.find('/somepath') >= 0, s)
        # The line number
        self.assertTrue(s.find('634') >= 0, s)
        # The column number
        self.assertTrue(s.find('57') >= 0, s)
        # The expression
        self.assertTrue(s.find("You're one in a million") >= 0, s)
        # The warning
        self.assertTrue(s.find("Repent, for the end is nigh") >= 0, s)


class ExceptionForTesting (Exception):
    pass


class TestingTracebackSupplement(object):
    source_url = '/somepath'
    line = 634
    column = 57
    warnings = ['Repent, for the end is nigh']
    def __init__(self, expression):
        self.expression = expression


class DummySupplement(object):
    pass


class DummyTB(object):
    tb_lineno = 14


class _Monkey(object):
    # context-manager for replacing module names in the scope of a test.
    def __init__(self, module, **kw):
        self.module = module
        self.to_restore = dict([(key, getattr(module, key, self))
                                    for key in kw])
        for key, value in kw.items():
            setattr(module, key, value)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for key, value in self.to_restore.items():
            if value is not self:
                setattr(self.module, key, value)
            else:
                delattr(self.module, key)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(Test_format_exception),
        unittest.makeSuite(Test_extract_stack),
    ))
