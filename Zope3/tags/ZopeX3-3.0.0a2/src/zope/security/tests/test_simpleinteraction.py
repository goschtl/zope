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
"""Unit tests for zope.security.simpleinteraction."""

import unittest

from zope.interface.verify import verifyObject


class RequestStub:

    def __init__(self, principal=None):
        self.principal = principal
        self.interaction = None


class TestInteraction(unittest.TestCase):

    def test(self):
        from zope.security.interfaces import IInteraction
        from zope.security.simpleinteraction import Interaction
        interaction = Interaction()
        verifyObject(IInteraction, interaction)

    def test_add(self):
        from zope.security.simpleinteraction import Interaction
        rq = RequestStub()
        interaction = Interaction()
        interaction.add(rq)
        self.assert_(rq in interaction.participations)
        self.assert_(rq.interaction is interaction)

        # rq already added
        self.assertRaises(ValueError, interaction.add, rq)

        interaction2 = Interaction()
        self.assertRaises(ValueError, interaction2.add, rq)

    def test_remove(self):
        from zope.security.simpleinteraction import Interaction
        rq = RequestStub()
        interaction = Interaction()

        self.assertRaises(ValueError, interaction.remove, rq)

        interaction.add(rq)

        interaction.remove(rq)
        self.assert_(rq not in interaction.participations)
        self.assert_(rq.interaction is None)

    def testCreateInteraction(self):
        from zope.security.interfaces import IInteraction
        from zope.security.simpleinteraction import createInteraction
        i1 = createInteraction()
        verifyObject(IInteraction, i1)
        self.assertEquals(list(i1.participations), [])

        user = object()
        request = RequestStub(user)
        i2 = createInteraction(request)
        verifyObject(IInteraction, i2)
        self.assertEquals(list(i2.participations), [request])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestInteraction))
    return suite


if __name__ == '__main__':
    unittest.main()
