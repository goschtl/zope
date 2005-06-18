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
"""PageletChooser tests

$Id$
"""
__docformat__ = 'restructuredtext'
import unittest
from zope.security.checker import defineChecker
from zope.testing.doctestunit import DocTestSuite


class TestMapping(object):
    def __init__(self, context=None):
        pass

    def _getAlias(self):
        """Return the macro name."""
        return 'testpagelet'

    alias = property(_getAlias)



def test_suite():
    return unittest.TestSuite((
        DocTestSuite('zope.app.pageletchooser.adapters'),
        DocTestSuite('zope.app.pageletchooser.collector'),
        DocTestSuite('zope.app.pageletchooser.vocabulary'),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
