##############################################################################
#
# Copyright (c) 2006 Lovely Systems and Contributors.
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
"""
$Id$
"""
__docformat__ = 'restructuredtext'

import unittest
from zope.app.testing import functional

functional.defineLayer('TestLayer', 'ftesting.zcml')


def setUp(test):
    """Setup a reasonable environment for the category tests"""
    pass

def setUpRamCache(test):
    """runs the configurator for a ram cache.
    """
    from zope.app.testing import functional
    root = functional.getRootFolder()
    from lovely.viewcache.configurator import RAMViewCacheConfigurator
    RAMViewCacheConfigurator(root)(None)
    test.globs['root']=root




def tearDown(test):
    pass


def test_suite():
    suite = unittest.TestSuite()
    suites = (
        functional.FunctionalDocFileSuite('README.txt', package='lovely.viewcache.stats',
                                          setUp=setUpRamCache),
        )
    for s in suites:
        s.layer=TestLayer
        suite.addTest(s)
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
