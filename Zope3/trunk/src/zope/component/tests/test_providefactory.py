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
"""Test the provideFactory method.

$Id: test_providefactory.py,v 1.2 2002/12/25 14:13:32 jim Exp $
"""


from unittest import TestCase, TestSuite, main, makeSuite
from zope.component.tests.placelesssetup import PlacelessSetup


class ProvideFactoryTestCase(PlacelessSetup, TestCase):

    def test_provide_factory(self):
        from zope.component import getService, createObject
        from zope.component.tests.factory import f, X, IX
        factories=getService(None, 'Factories')
        factories.provideFactory("Some.Object", f)
        thing = createObject(None,"Some.Object")
        self.assert_(isinstance(thing, X))


def test_suite():
    return makeSuite(ProvideFactoryTestCase)

if __name__=='__main__':
    main(defaultTest='test_suite')
