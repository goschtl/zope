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
from zope.testing import doctest
from transaction import abort

class FakeModule:
    def __init__(self, dict):
        self.__dict = dict
    def __getattr__(self, name):
        try:
            return self.__dict[name]
        except KeyError:
            raise AttributeError, name

name = 'zope.app.versioncontrol.README'

ps = PlacelessSetup()

def setUp(test):
    ps.setUp()
    dict = test.globs
    dict.clear()
    dict['__name__'] = name    
    sys.modules[name] = FakeModule(dict)

def tearDown(test):
    del sys.modules[name]
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

