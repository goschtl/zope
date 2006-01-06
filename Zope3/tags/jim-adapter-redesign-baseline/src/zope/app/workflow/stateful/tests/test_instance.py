##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Process Difinition Instance Tests

$Id$
"""
import unittest

from zope.interface import Interface, implements
from zope.interface.verify import verifyClass
from zope.schema import Text, Int

from zope.app.event.tests.placelesssetup import events, clearEvents
from zope.app.security.interfaces import IPermission
from zope.app.security.permission import Permission
from zope.security.checker import CheckerPublic
from zope.security.management import newInteraction, endInteraction

from zope.app.annotation.interfaces import IAttributeAnnotatable
from zope.app.component.interfaces.registration import IRegisterable
from zope.app.component.interfaces.registration import IRegistered
from zope.app.component.interfaces.registration import ActiveStatus

from zope.app.workflow.tests.workflowsetup import WorkflowSetup
from zope.app.workflow.interfaces import IProcessDefinition
from zope.app.workflow.instance import createProcessInstance
from zope.app.workflow.stateful.interfaces import IStatefulProcessInstance
from zope.app.workflow.stateful.interfaces import IBeforeTransitionEvent
from zope.app.workflow.stateful.interfaces import IAfterTransitionEvent
from zope.app.workflow.stateful.interfaces import IRelevantDataChangeEvent
from zope.app.workflow.stateful.interfaces import IBeforeRelevantDataChangeEvent
from zope.app.workflow.stateful.interfaces import IAfterRelevantDataChangeEvent
from zope.app.workflow.stateful.definition import StatefulProcessDefinition
from zope.app.workflow.stateful.definition import State, Transition
from zope.app.workflow.stateful.instance import StatefulProcessInstance
from zope.app.workflow.stateful.instance import StateChangeInfo

from zope.app import zapi
from zope.app.testing import ztapi
from zope.app.container.contained import contained
from zope.app.component.site import UtilityRegistration


class ParticipationStub(object):

    def __init__(self, principal):
        self.principal = principal
        self.interaction = None


# define and create ProcessDefinition (PD) for tests
class TestProcessDefinition(StatefulProcessDefinition):
    implements(IAttributeAnnotatable)


class ITestDataSchema(Interface):

    text = Text(title=u'a text', default=u'no text')

    value = Int(title=u'an int', default=1)


def sort(l):
    l.sort()
    return l


class SimpleProcessInstanceTests(WorkflowSetup, unittest.TestCase):

    def setUp(self):
        WorkflowSetup.setUp(self)

        pd = TestProcessDefinition()

        pd.setRelevantDataSchema(ITestDataSchema)

        pd.states['private'] = State()
        pd.states['published'] = State()
        pd.states['pending'] = State()

        pd.transitions['show'] = Transition('INITIAL', 'private')
        pd.transitions['publish_direct'] = Transition('private', 'published')
        pd.transitions['publish_pending'] = Transition('pending', 'published')
        pd.transitions['submit_pending'] = Transition('private', 'pending')
        pd.transitions['retract_published'] = Transition(
            'published', 'private')
        pd.transitions['retract_pending'] = Transition('pending', 'private')

        self.default['pd1'] = pd 

        name = self.cm.addRegistration(
            UtilityRegistration('definition1', IProcessDefinition,
                                self.default['pd1']))
        zapi.traverse(self.default.registrationManager,
                      name).status = ActiveStatus

        self.pd = self.sm.queryUtility(IProcessDefinition, 'definition1')
        # give the pi some context to find a utility
        self.pi = createProcessInstance(self.sm, 'definition1')
        # Let's also listen to the fired events
        clearEvents()


    def testInterface(self):
        verifyClass(IStatefulProcessInstance, StatefulProcessInstance)

    def testRelevantData(self):
        pi = self.pi
        data = pi.data

        self.assert_(ITestDataSchema.providedBy(data))

        self.assertEqual(data.text, 'no text')
        self.assertEqual(data.value, 1)

        self.assertNotEqual(data.__parent__, None)
        self.assertEqual(self.pi, self.pi.data.__parent__)

        data.text = 'another text'
        self.assert_(IBeforeRelevantDataChangeEvent.providedBy(events[0])) 
        self.assert_(IAfterRelevantDataChangeEvent.providedBy(events[-1])) 
        clearEvents()
        data.value = 10
        self.assert_(IBeforeRelevantDataChangeEvent.providedBy(events[0])) 
        self.assert_(IAfterRelevantDataChangeEvent.providedBy(events[-1])) 

        self.assertEqual(data.text, 'another text')
        self.assertEqual(data.value, 10)

    def testSimpleTranstitions(self):
        pi = self.pi
        pd = self.pd

        self.assertEqual(pi.status, pd.getInitialStateName())
        self.assertEqual(pi.getOutgoingTransitions(), ['show'])

        clearEvents()
        pi.fireTransition('show')
        self.assert_(IBeforeTransitionEvent.providedBy(events[0])) 
        self.assert_(IAfterTransitionEvent.providedBy(events[-1])) 
        self.assertEqual(pi.status, 'private')
        self.assertEqual(sort(pi.getOutgoingTransitions()),
                         ['publish_direct', 'submit_pending'])

        clearEvents()
        pi.fireTransition('submit_pending')
        self.assert_(IBeforeTransitionEvent.providedBy(events[0])) 
        self.assert_(IAfterTransitionEvent.providedBy(events[-1])) 
        self.assertEqual(pi.status, 'pending')
        self.assertEqual(sort(pi.getOutgoingTransitions()),
                         ['publish_pending', 'retract_pending'])

        clearEvents()
        pi.fireTransition('publish_pending')
        self.assert_(IBeforeTransitionEvent.providedBy(events[0])) 
        self.assert_(IAfterTransitionEvent.providedBy(events[-1])) 
        self.assertEqual(pi.status, 'published')
        self.assertEqual(sort(pi.getOutgoingTransitions()),
                         ['retract_published'])

        clearEvents()
        pi.fireTransition('retract_published')
        self.assert_(IBeforeTransitionEvent.providedBy(events[0])) 
        self.assert_(IAfterTransitionEvent.providedBy(events[-1])) 
        self.assertEqual(pi.status, 'private')

        clearEvents()
        pi.fireTransition('submit_pending')
        self.assert_(IBeforeTransitionEvent.providedBy(events[0])) 
        self.assert_(IAfterTransitionEvent.providedBy(events[-1])) 
        self.assertEqual(pi.status, 'pending')

        clearEvents()
        pi.fireTransition('retract_pending')
        self.assert_(IBeforeTransitionEvent.providedBy(events[0])) 
        self.assert_(IAfterTransitionEvent.providedBy(events[-1])) 
        self.assertEqual(pi.status, 'private')


class ConditionProcessInstanceTests(WorkflowSetup, unittest.TestCase):

    def setUp(self):
        WorkflowSetup.setUp(self)

        pd = TestProcessDefinition()

        pd.setRelevantDataSchema(ITestDataSchema)

        pd.states['state1'] = State()
        pd.states['state2'] = State()

        pd.transitions['initial_state1'] = Transition(
            'INITIAL', 'state1', condition='data/value')
        pd.transitions['initial_state2'] = Transition(
            'INITIAL', 'state2', condition='not: data/value')
        pd.transitions['state1_state2'] = Transition(
            'state1', 'state2', condition='python: data.text == "some text"')
        pd.transitions['state2_state1'] = Transition(
            'state2', 'state1', condition='python: data.text == "no text"')
        pd.transitions['state1_initial'] = Transition('state1', 'INITIAL')
        pd.transitions['state2_initial'] = Transition('state2', 'INITIAL')

        self.default['pd1'] = pd 

        n = self.cm.addRegistration(
            UtilityRegistration('definition1', IProcessDefinition,
                                self.default['pd1']))
        zapi.traverse(self.default.registrationManager, n
                      ).status = ActiveStatus

        self.pd = self.sm.queryUtility(IProcessDefinition, 'definition1')
        # give the pi some context to find a utility
        self.pi = contained(
            createProcessInstance(self.sm, 'definition1'),
            self.rootFolder)

    def testConditionalTranstitions(self):
        pi = self.pi
        pd = self.pd

        data = pi.data

        self.assertEqual(pi.status, pd.getInitialStateName())
        self.assertEqual(data.text, 'no text')
        self.assertEqual(data.value, 1)

        self.assertEqual(pi.getOutgoingTransitions(), ['initial_state1'])
        self.assertRaises(KeyError, pi.fireTransition, 'initial_state2')

        pi.fireTransition('initial_state1')
        self.assertEqual(pi.status, 'state1')
        self.assertEqual(pi.getOutgoingTransitions(), ['state1_initial'])

        data.text = 'some text'

        self.assertEqual(sort(pi.getOutgoingTransitions()),
                         ['state1_initial', 'state1_state2'])

        pi.fireTransition('state1_state2')
        self.assertEqual(pi.status, 'state2')
        self.assertEqual(pi.getOutgoingTransitions(), ['state2_initial'])
        self.assertRaises(KeyError, pi.fireTransition, 'state2_state1')

        data.text = 'no text'

        pi.fireTransition('state2_initial')
        self.assertEqual(pi.status, 'INITIAL')
        self.assertEqual(pi.getOutgoingTransitions(), ['initial_state1'])

        data.value = 0

        self.assertEqual(pi.getOutgoingTransitions(), ['initial_state2'])

        pi.fireTransition('initial_state2')
        self.assertEqual(pi.status, 'state2')
        self.assertEqual(pi.getOutgoingTransitions(),
                         ['state2_initial', 'state2_state1'])


def transition_script1(contexts):
    return contexts['data'].text == "some text"

def transition_script2(contexts):
    return contexts['data'].text == "no text"

class ScriptProcessInstanceTests(WorkflowSetup, unittest.TestCase):

    def setUp(self):
        WorkflowSetup.setUp(self)

        pd = TestProcessDefinition()

        pd.setRelevantDataSchema(ITestDataSchema)

        pd.states['state1'] = State()
        pd.states['state2'] = State()

        pd.transitions['initial_state1'] = Transition(
            'INITIAL', 'state1', script=lambda c: c['data'].value)
        pd.transitions['initial_state2'] = Transition(
            'INITIAL', 'state2', script=lambda c: not c['data'].value)
        pd.transitions['state1_state2'] = Transition(
            'state1', 'state2', script=transition_script1)
        pd.transitions['state2_state1'] = Transition(
            'state2', 'state1', script=transition_script2)
        pd.transitions['state1_initial'] = Transition('state1', 'INITIAL')
        pd.transitions['state2_initial'] = Transition('state2', 'INITIAL')

        self.default['pd1'] = pd 

        k = self.cm.addRegistration(
            UtilityRegistration('definition1', IProcessDefinition,
                                self.default['pd1']))
        zapi.traverse(self.default.registrationManager,
                      k).status = ActiveStatus

        self.pd = self.sm.queryUtility(IProcessDefinition, 'definition1')
        # give the pi some context to find a utility
        self.pi = contained(
            createProcessInstance(self.sm, 'definition1'),
            self.rootFolder)

    def testConditionalTranstitions(self):
        pi = self.pi
        pd = self.pd

        data = pi.data

        self.assertEqual(pi.status, pd.getInitialStateName())
        self.assertEqual(data.text, 'no text')
        self.assertEqual(data.value, 1)

        self.assertEqual(pi.getOutgoingTransitions(), ['initial_state1'])
        self.assertRaises(KeyError, pi.fireTransition, 'initial_state2')

        pi.fireTransition('initial_state1')
        self.assertEqual(pi.status, 'state1')
        self.assertEqual(pi.getOutgoingTransitions(), ['state1_initial'])

        data.text = 'some text'

        self.assertEqual(sort(pi.getOutgoingTransitions()),
                         ['state1_initial', 'state1_state2'])

        pi.fireTransition('state1_state2')
        self.assertEqual(pi.status, 'state2')
        self.assertEqual(pi.getOutgoingTransitions(), ['state2_initial'])
        self.assertRaises(KeyError, pi.fireTransition, 'state2_state1')

        data.text = 'no text'

        pi.fireTransition('state2_initial')
        self.assertEqual(pi.status, 'INITIAL')
        self.assertEqual(pi.getOutgoingTransitions(), ['initial_state1'])

        data.value = 0

        self.assertEqual(pi.getOutgoingTransitions(), ['initial_state2'])

        pi.fireTransition('initial_state2')
        self.assertEqual(pi.status, 'state2')
        self.assertEqual(pi.getOutgoingTransitions(),
                         ['state2_initial', 'state2_state1'])


class PermissionProcessInstanceTests(WorkflowSetup, unittest.TestCase):

    def setUp(self):
        WorkflowSetup.setUp(self)

        ztapi.provideUtility(IPermission, Permission('deny', 'Deny'), 'deny')

        endInteraction()
        newInteraction(ParticipationStub('test'))

        pd = TestProcessDefinition()

        pd.setRelevantDataSchema(ITestDataSchema)

        pd.states['state1'] = State()
        pd.states['state2'] = State()

        pd.transitions['initial_state1'] = Transition(
            'INITIAL', 'state1', permission=CheckerPublic)
        pd.transitions['initial_state2'] = Transition(
            'INITIAL', 'state2', permission='deny')
        pd.transitions['state1_state2'] = Transition(
            'state1', 'state2', permission=CheckerPublic)
        pd.transitions['state2_state1'] = Transition('state2', 'state1')
        pd.transitions['state1_initial'] = Transition(
            'state1', 'INITIAL', permission='deny')
        pd.transitions['state2_initial'] = Transition(
            'state2', 'INITIAL', permission=CheckerPublic)

        self.default['pd1'] = pd 

        k = self.cm.addRegistration(
            UtilityRegistration('definition1', IProcessDefinition,
                                self.default['pd1']))
        zapi.traverse(self.default.registrationManager,
                      k).status = ActiveStatus

        self.pd = self.sm.queryUtility(IProcessDefinition, 'definition1')
        # give the process instance container (pic) some context to find a
        # utility (while this is not correct, it resembles the current
        # behavior.
        from zope.app.workflow.instance import ProcessInstanceContainerAdapter
        pic = ProcessInstanceContainerAdapter(self.rootFolder)
        self.pi = contained(
            createProcessInstance(self.sm, 'definition1'),
            pic)

    def testPermissionedTranstitions(self):
        pi = self.pi
        pd = self.pd

        self.assertEqual(pi.status, pd.getInitialStateName())

        self.assertEqual(pi.getOutgoingTransitions(), ['initial_state1'])
        self.assertRaises(KeyError, pi.fireTransition, 'initial_state2')

        pi.fireTransition('initial_state1')
        self.assertEqual(pi.status, 'state1')
        self.assertEqual(pi.getOutgoingTransitions(), ['state1_state2'])


class DummyTransition(object):
    def __init__(self, source, destination):
        self.sourceState = source
        self.destinationState = destination


class TestStateChangeInfo(unittest.TestCase):

    def testStateChangeInfo(self):
        t = DummyTransition(1,2)
        sci = StateChangeInfo(t)
        self.assertEqual(sci.old_state, 1)
        self.assertEqual(sci.new_state, 2)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(SimpleProcessInstanceTests),
        unittest.makeSuite(ConditionProcessInstanceTests),
        unittest.makeSuite(ScriptProcessInstanceTests),
        unittest.makeSuite(PermissionProcessInstanceTests),
        unittest.makeSuite(TestStateChangeInfo),
        ))

if __name__ == '__main__':
    unittest.main()
