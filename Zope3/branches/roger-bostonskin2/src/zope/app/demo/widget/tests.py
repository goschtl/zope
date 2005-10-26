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
"""Demo widget implementation

$Id$
"""

import unittest
from zope.testing.doctestunit import DocTestSuite
from zope.testing.doctestunit import DocFileSuite


def test_suite():
    return unittest.TestSuite((
        DocTestSuite('zope.app.demo.widget.boolwidget'),
        DocTestSuite('zope.app.demo.widget.intwidget'),
        DocTestSuite('zope.app.demo.widget.textwidget'),
        DocTestSuite('zope.app.demo.widget.textareawidget'),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
