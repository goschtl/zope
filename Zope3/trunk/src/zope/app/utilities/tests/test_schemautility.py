##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""
$Id: test_schemautility.py,v 1.1 2003/08/07 20:42:00 sidnei Exp $
"""

from unittest import TestCase, makeSuite, TestSuite
from zope.app.utilities.schema import SchemaUtility
from zope.schema import Text, getFieldsInOrder, getFieldNamesInOrder

class SchemaUtilityTests(TestCase):

    def setUp(self):
        self.s = SchemaUtility('IFoo')
        self.alpha = Text(title=u"alpha")

    def test_addField(self):
        s = self.s
        s.addField('alpha', self.alpha)
        self.assertEquals(
            [('alpha', self.alpha)],
            getFieldsInOrder(s))

    def test_removeField(self):
        s = self.s
        s.addField('alpha', self.alpha)
        s.removeField('alpha')
        self.assertEquals(
            [],
            getFieldsInOrder(s))

    def test_addFieldCollision(self):
        s = self.s
        s.addField('alpha', self.alpha)
        self.assertRaises(KeyError, s.addField, 'alpha', self.alpha)

    def test_removeFieldNotPresent(self):
        self.assertRaises(KeyError, self.s.removeField, 'alpha')

    def test_renameField(self):
        s = self.s
        s.addField('alpha', self.alpha)
        s.renameField('alpha', 'beta')
        self.assertEquals(
            [('beta', self.alpha)],
            getFieldsInOrder(s))

    def test_renameFieldCollision(self):
        s = self.s
        s.addField('alpha', self.alpha)
        s.addField('beta', Text(title=u"Beta"))
        self.assertRaises(KeyError, s.renameField, 'alpha', 'beta')

    def test_renameFieldNotPresent(self):
        self.assertRaises(KeyError, self.s.renameField, 'alpha', 'beta')

    def test_insertField(self):
        s = self.s
        s.addField('alpha', self.alpha)
        beta = Text(title=u"Beta")
        s.insertField('beta', beta, 0)
        self.assertEquals(
            [('beta', beta),
             ('alpha', self.alpha)],
            getFieldsInOrder(s))

    def test_insertFieldCollision(self):
        s = self.s
        s.addField('alpha', self.alpha)
        beta = Text(title=u"Beta")
        self.assertRaises(KeyError, s.insertField, 'alpha', beta, 0)

    def test_insertFieldCornerCases(self):
        s = self.s
        gamma = Text(title=u"Gamma")
        # it's still possible to insert at beginning
        s.insertField('gamma', gamma, 0)
        self.assertEquals(
            [('gamma', gamma)],
            getFieldsInOrder(s))
        # should be allowed to insert field at the end
        s.insertField('alpha', self.alpha, 1)
        self.assertEquals(
            [('gamma', gamma),
             ('alpha', self.alpha)],
            getFieldsInOrder(s))
        # should be allowed to insert field at the beginning still
        delta = Text(title=u"Delta")
        s.insertField('delta', delta, 0)
        self.assertEquals(
            [('delta', delta),
             ('gamma', gamma),
             ('alpha', self.alpha)],
            getFieldsInOrder(s))

    def test_insertFieldBeyondEnd(self):
        s = self.s
        s.addField('alpha', self.alpha)
        beta = Text(title=u"Beta")
        self.assertRaises(IndexError, s.insertField,
                          'beta', beta, 100)

    def test_insertFieldBeforeBeginning(self):
        s = self.s
        s.addField('alpha', self.alpha)
        beta = Text(title=u"Beta")
        self.assertRaises(IndexError, s.insertField,
                          'beta', beta, -1)

    def test_moveField(self):
        s = self.s
        s.addField('alpha', self.alpha)
        beta = Text(title=u'Beta')
        s.addField('beta', beta)
        gamma = Text(title=u'Gamma')
        s.addField('gamma', gamma)
        s.moveField('beta', 3)
        self.assertEquals(
            [('alpha', self.alpha),
             ('gamma', gamma),
             ('beta', beta)],
            getFieldsInOrder(s))

    def test_moveFieldBeyondEnd(self):
        s = self.s
        s.addField('alpha', self.alpha)
        beta = Text(title=u"Beta")
        s.addField('beta', beta)
        self.assertRaises(IndexError, s.moveField,
                          'beta', 100)

    def test_moveFieldBeforeBeginning(self):
        s = self.s
        s.addField('alpha', self.alpha)
        beta = Text(title=u"Beta")
        s.addField('beta', beta)
        self.assertRaises(IndexError, s.moveField,
                          'beta', -1)


def test_suite():
    return TestSuite(
        (makeSuite(SchemaUtilityTests),
         ))
