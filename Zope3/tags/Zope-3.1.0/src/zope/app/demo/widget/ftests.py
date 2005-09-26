##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Functional doc tests for demo widget implementation

$Id$
"""

import unittest
from zope.app.testing import functional

def test_suite():
    return unittest.TestSuite((
        functional.FunctionalDocFileSuite('./help/boolwidget.txt'),
        functional.FunctionalDocFileSuite('./help/intwidget.txt'),
        functional.FunctionalDocFileSuite('./help/textwidget.txt'),
        functional.FunctionalDocFileSuite('./help/textareawidget.txt'),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
