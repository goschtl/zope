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
import zope.app.location
import zope.app.versioncontrol.version

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



def testLocationSanity_for_cloneByPickle():
    """\
cloneByPickle should not go outside a location

    >>> parent = zope.app.location.Location()
    >>> parent.poison = lambda: None
    >>> ob = zope.app.location.Location()
    >>> ob.__parent__ = parent
    >>> x = zope.app.location.Location()
    >>> x.poison = lambda: None
    >>> ob.x = x
    >>> ob.y = zope.app.location.Location()
    >>> ob.y.__parent__ = ob
    >>> clone = zope.app.versioncontrol.version.cloneByPickle(ob)
    >>> clone.__parent__ is ob.__parent__
    True
    >>> clone.x is ob.x
    True
    >>> clone.y is ob.y
    False

"""
    

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt',
                             setUp=setUp, tearDown=tearDown,
                             ),
        doctest.DocTestSuite(),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

