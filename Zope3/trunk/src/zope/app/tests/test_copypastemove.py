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
"""XXX short summary goes here.

$Id: test_copypastemove.py,v 1.1 2003/09/21 17:33:34 jim Exp $
"""
import unittest
from zope.testing.doctestunit import DocTestSuite
from zope.app.tests.placelesssetup import setUp, tearDown

def test_suite():
    return unittest.TestSuite((
        DocTestSuite('zope.app.copypastemove',
                     setUp=setUp, tearDown=tearDown),
        ))

if __name__ == '__main__': unittest.main()
