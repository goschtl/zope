##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Doc test harness for queryType function.

$Id: test_queryinterface.py,v 1.1 2004/03/20 22:08:26 nathan Exp $
"""
import unittest
from zope.testing.doctestunit import DocTestSuite
from zope.interface import Interface

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(DocTestSuite("zope.app.interface"))
    
    return suite


if __name__ == '__main__':
    unittest.main()
