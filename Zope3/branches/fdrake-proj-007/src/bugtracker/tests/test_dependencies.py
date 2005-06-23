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
"""Bug Dependencies Tests

$Id: test_dependencies.py,v 1.3 2003/08/28 05:22:32 srichter Exp $
"""
import unittest

from zope.interface import classImplements
from zope.component.tests.placelesssetup import PlacelessSetup

from zope.app.testing import ztapi
from zope.app.annotation.interfaces import IAnnotations, IAttributeAnnotatable
from zope.app.annotation.attribute import AttributeAnnotations
from zope.app.location.interfaces import ILocation
from zope.app.location.traversing import LocationPhysicallyLocatable
from zope.app.traversing.interfaces import IPhysicallyLocatable

from bugtracker.interfaces import IBug, IBugDependencies
from bugtracker.bug import Bug, BugDependencyAdapter
from bugtracker.tracker import BugTracker


class DependencyTest(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(DependencyTest, self).setUp()
        classImplements(Bug, IAttributeAnnotatable);
        ztapi.provideAdapter(IAttributeAnnotatable, IAnnotations,
                             AttributeAnnotations)
        ztapi.provideAdapter(IBug, IBugDependencies,
                             BugDependencyAdapter)
        ztapi.provideAdapter(ILocation, IPhysicallyLocatable,
                             LocationPhysicallyLocatable)

        self.bug = Bug()

    def makeTestObject(self):
        return BugDependencyAdapter(self.bug)

    def test_Interface(self):
        deps = self.makeTestObject()
        self.failUnless(IBugDependencies.providedBy(deps))

    def test_dependencies(self):
        deps = self.makeTestObject()
        self.assertEqual((), deps.dependencies)
        deps.dependencies = ('foo',)
        self.assertEqual(('foo',), deps.dependencies)
        deps.addDependencies(('foobar',))
        self.assertEqual(('foo', 'foobar'), deps.dependencies)
        deps.deleteDependencies(('foobar',))
        self.assertEqual(('foo',), deps.dependencies)
        # Test whether the annotations stay.
        deps = self.makeTestObject()
        self.assertEqual(('foo',), deps.dependencies)

    def test_findChildren(self):
        tracker = BugTracker()

        bug1 = Bug()
        tracker['1'] = bug1
        deps1 = BugDependencyAdapter(bug1)

        bug2 = Bug()
        tracker['2'] = bug2
        deps2 = BugDependencyAdapter(bug2)
        deps1.dependencies = ('2',)

        bug3 = Bug()
        tracker['3'] = bug3
        deps2.dependencies = ('3',)

        self.assertEqual(( (bug2, ()), ),
                         deps1.findChildren(False));

        self.assertEqual(((bug2, ((bug3, ()),) ),),
                         deps1.findChildren());
        
    
def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(DependencyTest),
        ))

if __name__ == '__main__':
    unittest.main()
