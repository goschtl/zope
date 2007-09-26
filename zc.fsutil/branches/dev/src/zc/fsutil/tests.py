##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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
import time, unittest
from zope.testing import doctest
import zope.testing.setupstack



def setUp(test):
    zope.testing.setupstack.setUpDirectory(test)
    orig_time = time.time
    def restore_time_time():
        time.time = orig_time
    zope.testing.setupstack.register(test, restore_time_time)
    time.time = lambda : 1190753032.5621099
    
    


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'references.txt',
            setUp=setUp, tearDown=zope.testing.setupstack.tearDown,
            ),
        ))

