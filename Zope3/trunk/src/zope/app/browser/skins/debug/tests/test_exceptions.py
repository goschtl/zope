##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
""" Unit tests for the 'exceptions' view.

Revision information:
$Id: test_exceptions.py,v 1.2 2003/03/12 14:35:50 tseaver Exp $
"""

from unittest import TestCase, TestLoader, TextTestRunner

class TestExceptions(TestCase):
    
    def _getTargetClass(self):
        from zope.app.browser.skins.debug.exceptions import ExceptionDebugView
        return ExceptionDebugView

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_tracebackLines(self):
        import sys
        import traceback
        try:
            1/0
        except:
            context = sys.exc_info()[0]
            request = None
            view = self._makeOne(context, request)
            self.assertEqual(view.error_type, sys.exc_info()[0])
            self.assertEqual(view.error_object, sys.exc_info()[1])
            tb_lines = traceback.extract_tb(sys.exc_info()[2])
            self.assertEqual(len(view.traceback_lines), len(tb_lines))

def test_suite():
    loader = TestLoader()
    return loader.loadTestsFromTestCase(TestExceptions)

if __name__=='__main__':
    TextTestRunner().run(test_suite())

