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

"""Stateful workflow process definition.

$Id: test_definition.py,v 1.1 2003/05/08 17:27:20 jack-e Exp $
"""
import unittest

from zope.interface import Interface
from zope.interface.verify import verifyClass
from zope.schema import TextLine

from zope.app.interfaces.workflow.stateful import IStatefulProcessDefinition
from zope.app.workflow.stateful.definition import StatefulProcessDefinition


class IDummyState(Interface):
    """A really dummy state"""

class DummyState:
    __implements__ = IDummyState


class IDummyTransition(Interface):
    """A really dummy transition"""

class DummyTransition:
    __implements__ = IDummyTransition


class IDummyDataSchema(Interface):

    text = TextLine(title=u'a text', default=u'no text')
    

# XXX Tests missing for:
# State Class/Interface
# Transition Class/Interface


class StatefulProcessDefinitionTests(unittest.TestCase):

    def setUp(self):
        self.pd = pd = StatefulProcessDefinition()
        self.doMinimalSetup()

    def doMinimalSetup(self):
        pd = self.pd
        pd.setRelevantDataSchema(IDummyDataSchema)
        self.st1 = st1 = DummyState()
        self.st2 = st2 = DummyState()
        pd.addState('st1', st1)
        pd.addState('st2', st2)

        self.tr1 = tr1 = DummyTransition()
        self.tr2 = tr2 = DummyTransition()
        pd.addTransition('tr1', tr1)
        pd.addTransition('tr2', tr2)

    def testInterface(self):
        verifyClass(IStatefulProcessDefinition, StatefulProcessDefinition)

    def testGetSchema(self):
        self.assertEqual(self.pd.getRelevantDataSchema(), IDummyDataSchema)

    def testGetStateNames(self):
        pd = self.pd

        names = pd.getStateNames()

        self.failUnless('st1' in names)
        self.failUnless('st2' in names)
        self.failUnless(pd.getInitialStateName() in names)

    def testGetState(self):
        pd = self.pd

        st1 = pd.getState('st1')

        self.assertEqual(st1, self.st1)

    def testRemoveState(self):
        pd = self.pd

        pd.removeState('st1')
        names = pd.getStateNames()

        self.assertRaises(KeyError, pd.getState, 'st1')
        self.failIf('st1' in names)
        self.failUnless('st2' in names)
        self.failUnless(pd.getInitialStateName() in names)
        
    def testGetTransistionNames(self):
        pd = self.pd

        names = pd.getTransitionNames()

        self.failUnless('tr1' in names)
        self.failUnless('tr2' in names)

    def testGetTransation(self):
        pd = self.pd

        tr1 = pd.getTransition('tr1')

        self.assertEqual(tr1, self.tr1)

    def testRemoveTransistion(self):
        pd = self.pd

        pd.removeTransition('tr1')
        names = pd.getTransitionNames()

        self.assertRaises(KeyError, pd.getTransition, 'tr1')
        self.failIf('tr1' in names)
        self.failUnless('tr2' in names)

    # this needs a rather complicated setup
    # that is done in the test_instance.py tests
    # can we leave this test out in here ??
    def tobedone_testCreateProcessInstance(self):
        pass

class StatefulProcessDefinitionAttributesTests(unittest.TestCase):

    def setUp(self):
        self.pd = pd = StatefulProcessDefinition()
        self.doMinimalSetup()

    def doMinimalSetup(self):
        pd = self.pd
        self.st1 = st1 = DummyState()
        self.st2 = st2 = DummyState()
        pd.states.setObject('st1', st1)
        pd.states.setObject('st2', st2)

        self.tr1 = tr1 = DummyTransition()
        self.tr2 = tr2 = DummyTransition()
        pd.transitions.setObject('tr1', tr1)
        pd.transitions.setObject('tr2', tr2)

    def testInterface(self):
        verifyClass(IStatefulProcessDefinition, StatefulProcessDefinition)

    def testGetStateNames(self):
        pd = self.pd

        names = pd.states.keys()

        self.failUnless('st1' in names)
        self.failUnless('st2' in names)
        self.failUnless(pd.getInitialStateName() in names)

    def testGetState(self):
        pd = self.pd

        st1 = pd.states['st1']

        self.assertEqual(st1, self.st1)

    def testRemoveState(self):
        pd = self.pd

        del pd.states['st1']
        names = pd.getStateNames()

        self.assertRaises(KeyError, pd.states.__getitem__, 'st1')
        self.failIf('st1' in names)
        self.failUnless('st2' in names)
        self.failUnless(pd.getInitialStateName() in names)
        
    def testGetTransistionNames(self):
        pd = self.pd

        names = pd.transitions.keys()

        self.failUnless('tr1' in names)
        self.failUnless('tr2' in names)

    def testGetTransation(self):
        pd = self.pd

        tr1 = pd.transitions['tr1']

        self.assertEqual(tr1, self.tr1)

    def testRemoveTransistion(self):
        pd = self.pd

        del pd.transitions['tr1']
        names = pd.transitions.keys()

        self.assertRaises(KeyError, pd.transitions.__getitem__, 'tr1')
        self.failIf('tr1' in names)
        self.failUnless('tr2' in names)



def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(StatefulProcessDefinitionTests),
        unittest.makeSuite(StatefulProcessDefinitionAttributesTests),
        ))

if __name__ == '__main__':
    unittest.main()
