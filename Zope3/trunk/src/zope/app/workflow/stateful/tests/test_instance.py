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
"""Process Difinition Instance Tests

$Id: test_instance.py,v 1.10 2003/12/15 13:33:17 srichter Exp $
"""

import unittest

from zope.interface import Interface, implements
from zope.interface.verify import verifyClass
from zope.schema import Text, Int

from zope.component.service import serviceManager
from zope.app.event.tests.placelesssetup import \
     eventPublisher, EventRecorder, events, clearEvents
from zope.app.interfaces.security import IPermissionService
from zope.app.security.registries.permissionregistry \
     import permissionRegistry
from zope.app.services.servicenames import Permissions
from zope.security.checker import CheckerPublic
from zope.security.management import newSecurityManager

from zope.app.interfaces.services.registration import IRegisterable
from zope.app.interfaces.services.registration import IRegistered
from zope.app.interfaces.annotation import IAttributeAnnotatable
from zope.app.interfaces.services.registration import ActiveStatus

from zope.app.workflow.tests.workflowsetup import WorkflowSetup
from zope.app.workflow.service import ProcessDefinitionRegistration
from zope.app.interfaces.workflow.stateful \
     import IStatefulProcessInstance
from zope.app.interfaces.workflow.stateful import \
     IBeforeTransitionEvent, IAfterTransitionEvent
from zope.app.interfaces.workflow.stateful import IRelevantDataChangeEvent
from zope.app.interfaces.workflow.stateful import \
     IBeforeRelevantDataChangeEvent, IAfterRelevantDataChangeEvent
from zope.app.workflow.stateful.definition \
     import StatefulProcessDefinition, State, Transition
from zope.app.workflow.stateful.instance \
     import StatefulProcessInstance, StateChangeInfo
from zope.app import zapi
from zope.app.container.contained import contained


# define and create ProcessDefinition (PD) for tests
class TestProcessDefinition(StatefulProcessDefinition):
    implements(IAttributeAnnotatable, IRegisterable, IRegistered)

    # Incompletely implementing IRegistered
    def addUsage(self, location):
        pass

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
            ProcessDefinitionRegistration('definition1',
                                          '/++etc++site/default/pd1'))
        zapi.traverse(self.default.getRegistrationManager(),
                      name).status = ActiveStatus

        self.pd = self.service.getProcessDefinition('definition1')
        # give the pi some context to find a service
        self.pi = self.service.createProcessInstance('definition1')
        # Let's also listen to the fired events
        clearEvents()
        eventPublisher.globalSubscribe(EventRecorder)


    def testInterface(self):
        verifyClass(IStatefulProcessInstance, StatefulProcessInstance)

    def testRelevantData(self):
        pi = self.pi
        data = pi.data

        self.assert_(ITestDataSchema.isImplementedBy(data))

        self.assertEqual(data.text, 'no text')
        self.assertEqual(data.value, 1)

        data.text = 'another text'
        self.assert_(IBeforeRelevantDataChangeEvent.isImplementedBy(events[0])) 
        self.assert_(IAfterRelevantDataChangeEvent.isImplementedBy(events[-1])) 
        clearEvents()
        data.value = 10
        self.assert_(IBeforeRelevantDataChangeEvent.isImplementedBy(events[0])) 
        self.assert_(IAfterRelevantDataChangeEvent.isImplementedBy(events[-1])) 

        self.assertEqual(data.text, 'another text')
        self.assertEqual(data.value, 10)

    def testSimpleTranstitions(self):
        pi = self.pi
        pd = self.pd

        self.assertEqual(pi.status, pd.getInitialStateName())
        self.assertEqual(pi.getOutgoingTransitions(), ['show'])

        clearEvents()
        pi.fireTransition('show')
        self.assert_(IBeforeTransitionEvent.isImplementedBy(events[0])) 
        self.assert_(IAfterTransitionEvent.isImplementedBy(events[-1])) 
        self.assertEqual(pi.status, 'private')
        self.assertEqual(sort(pi.getOutgoingTransitions()),
                         ['publish_direct', 'submit_pending'])

        clearEvents()
        pi.fireTransition('submit_pending')
        self.assert_(IBeforeTransitionEvent.isImplementedBy(events[0])) 
        self.assert_(IAfterTransitionEvent.isImplementedBy(events[-1])) 
        self.assertEqual(pi.status, 'pending')
        self.assertEqual(sort(pi.getOutgoingTransitions()),
                         ['publish_pending', 'retract_pending'])

        clearEvents()
        pi.fireTransition('publish_pending')
        self.assert_(IBeforeTransitionEvent.isImplementedBy(events[0])) 
        self.assert_(IAfterTransitionEvent.isImplementedBy(events[-1])) 
        self.assertEqual(pi.status, 'published')
        self.assertEqual(sort(pi.getOutgoingTransitions()),
                         ['retract_published'])

        clearEvents()
        pi.fireTransition('retract_published')
        self.assert_(IBeforeTransitionEvent.isImplementedBy(events[0])) 
        self.assert_(IAfterTransitionEvent.isImplementedBy(events[-1])) 
        self.assertEqual(pi.status, 'private')

        clearEvents()
        pi.fireTransition('submit_pending')
        self.assert_(IBeforeTransitionEvent.isImplementedBy(events[0])) 
        self.assert_(IAfterTransitionEvent.isImplementedBy(events[-1])) 
        self.assertEqual(pi.status, 'pending')

        clearEvents()
        pi.fireTransition('retract_pending')
        self.assert_(IBeforeTransitionEvent.isImplementedBy(events[0])) 
        self.assert_(IAfterTransitionEvent.isImplementedBy(events[-1])) 
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
            ProcessDefinitionRegistration('definition1',
                                          '/++etc++site/default/pd1'))
        zapi.traverse(self.default.getRegistrationManager(), n
                      ).status = ActiveStatus

        self.pd = self.service.getProcessDefinition('definition1')
        # give the pi some context to find a service
        self.pi = contained(
            self.service.createProcessInstance('definition1'),
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
            ProcessDefinitionRegistration('definition1',
                                          '/++etc++site/default/pd1'))
        zapi.traverse(self.default.getRegistrationManager(),
                      k).status = ActiveStatus

        self.pd = self.service.getProcessDefinition('definition1')
        # give the pi some context to find a service
        self.pi = contained(
            self.service.createProcessInstance('definition1'),
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

        serviceManager.defineService(Permissions, IPermissionService)
        serviceManager.provideService(Permissions, permissionRegistry)
        permissionRegistry.definePermission('deny', 'Deny')

        #newSecurityManager(system_user)
        newSecurityManager('test')

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
            ProcessDefinitionRegistration('definition1',
                                          '/++etc++site/default/pd1'))
        zapi.traverse(self.default.getRegistrationManager(),
                      k).status = ActiveStatus

        self.pd = self.service.getProcessDefinition('definition1')
        # give the process instance container (pic) some context to find a
        # service (while this is not correct, it resembles the current
        # behavior.
        from zope.app.workflow.instance import ProcessInstanceContainerAdapter
        pic = ProcessInstanceContainerAdapter(self.rootFolder)
        self.pi = contained(
            self.service.createProcessInstance('definition1'),
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


class DummyTransition:
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
