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
"""Groups folder tests.

$Id: tests.py 27237 2004-10-12 10:49:00 mriya3 $
"""

__docformat__ = "reStructuredText"
import unittest
from zope.testing import doctest
from zope.schema.interfaces import ITextLine
from zope.app.tests import placelesssetup
from zope.app.tests import ztapi
from zope.app.form.browser import TextWidget
from zope.app.form.interfaces import IInputWidget

def setUp(test):
    placelesssetup.setUp()
    ztapi.browserView(ITextLine, '', TextWidget, providing=IInputWidget)

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('groupsfolder.txt',
                             setUp=setUp, tearDown=placelesssetup.tearDown),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')









"""

import unittest
from zope.testing.doctest import DocFileSuite

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(DocFileSuite('groupsfolder.txt'))
    return suite
        
    
"""
