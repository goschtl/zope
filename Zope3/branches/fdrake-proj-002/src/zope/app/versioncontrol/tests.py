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
"""Version control tests

$Id$
"""
import sys
import unittest

from zope.component.tests.placelesssetup import PlacelessSetup
from zope.testing import doctest, module
from transaction import abort

name = 'zope.app.versioncontrol.README'

ps = PlacelessSetup()

def setUp(test):
    ps.setUp()
    module.setUp(test, name)

def tearDown(test):
    module.tearDown(test, name)
    abort()
    db = test.globs.get('db')
    if db is not None:
        db.close()
    ps.tearDown()

def test_suite():
    return doctest.DocFileSuite('README.txt',
                                setUp=setUp, tearDown=tearDown,
                                )

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

