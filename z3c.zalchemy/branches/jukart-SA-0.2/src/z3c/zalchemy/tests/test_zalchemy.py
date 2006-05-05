##############################################################################
#
# Copyright (c) 2006 ROBOTECH Logistiksysteme GmbH and Contributors.
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

import unittest
from zope.testing.doctestunit import DocFileSuite

def test_suite():
    return unittest.TestSuite((
            DocFileSuite('TRANSACTION.txt'),
            DocFileSuite('../README.txt'),
            ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

