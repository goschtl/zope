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
$Id: test_doctests.py,v 1.1 2003/07/22 10:05:54 Zen Exp $
"""

import unittest
from zope.testing.doctestunit import DocTestSuite
import zope.app.rdb

def test_suite():
    return DocTestSuite(module=zope.app.rdb)

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
