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
import persistent

from zope import component, interface
from zope.component.tests.placelesssetup import PlacelessSetup
from zope.testing import doctest, module
from transaction import abort
import zope.app.annotation.interfaces
import zope.app.annotation.attribute
import zope.app.location
import zope.app.versioncontrol.version
from zope.app.versioncontrol import interfaces, nonversioned
import zope.app.traversing.interfaces

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


class L(persistent.Persistent, zope.app.location.Location):
    interface.implements(interfaces.IVersionable,
                         zope.app.annotation.interfaces.IAttributeAnnotatable,
                         zope.app.traversing.interfaces.IPhysicallyLocatable,
                         )
    def getPath(self):
        return 'whatever'


def testLocationSanity_for__findModificationTime():
    """\
_findModificationTime should not go outside the location

    >>> import ZODB.tests.util
    >>> db = ZODB.tests.util.DB()
    >>> conn = db.open()


    >>> ob = L()
    >>> conn.root()['ob'] = ob
    >>> ob.y = L()
    >>> ob.y.__parent__ = ob
    >>> parent = L()
    >>> ob.__parent__ = parent
    >>> x = L()
    >>> ob.x = x

    >>> import transaction
    >>> transaction.commit()

    >>> parent.v = 1
    >>> transaction.commit()

    >>> import zope.app.versioncontrol.utility
    >>> p = zope.app.versioncontrol.utility._findModificationTime(ob)
    >>> p == ob._p_serial == ob.y._p_serial
    True

    >>> ob.x.v = 1
    >>> transaction.commit()

    >>> p = zope.app.versioncontrol.utility._findModificationTime(ob)
    >>> p == ob._p_serial == ob.y._p_serial
    True

    >>> ob.y.v = 1
    >>> transaction.commit()

    >>> p = zope.app.versioncontrol.utility._findModificationTime(ob)
    >>> p == ob._p_serial
    False
    >>> p == ob.y._p_serial
    True
    
"""

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

def test_isResourceChanged_works_with_ghosts():
    """\

There was a bug that caused isResourceChanged to give an incorrect
answer when applied to an object who's verion info was a ghost.

Let's create an object, put it under vc and make sure that
isResourceChanged works as expected:

    >>> from ZODB.tests import util
    >>> import transaction
    >>> db = util.DB()
    >>> component.provideAdapter(
    ...     zope.app.annotation.attribute.AttributeAnnotations)
    >>> component.provideAdapter(
    ...     nonversioned.StandardNonVersionedDataAdapter,
    ...     [None])
    >>> import zope.app.versioncontrol.repository
    >>> import zope.interface.verify

    >>> import zope.security.testing
    >>> principal = zope.security.testing.Principal('bob')
    >>> participation = zope.security.testing.Participation(principal)

    >>> import zope.security.management
    >>> zope.security.management.newInteraction(participation)

    >>> repository = zope.app.versioncontrol.repository.Repository()
    >>> ob = L()
    >>> conn1 = db.open()
    >>> conn1.root()['ob'] = ob
    >>> repository.applyVersionControl(ob, 'initial')
    >>> transaction.commit()
    >>> repository.isResourceChanged(ob)
    False

    >>> ob.x = 1
    >>> transaction.commit()
    >>> repository.isResourceChanged(ob) # eek
    True
    >>> repository.checkoutResource(ob)
    >>> repository.checkinResource(ob)
    >>> transaction.commit()
    >>> repository.isResourceChanged(ob)
    False

So far so good.  Now, we'll open a new connection and see if we get
the right answer:
    
    >>> conn2 = db.open()
    >>> ob = conn2.root()['ob']
    >>> repository.isResourceChanged(ob)
    False
    
    >>> zope.security.management.endInteraction()

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

