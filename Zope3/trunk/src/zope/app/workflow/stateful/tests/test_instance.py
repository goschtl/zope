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
"""

Revision information:
$Id: test_instance.py,v 1.1 2003/05/08 17:27:20 jack-e Exp $
"""

import unittest

from zope.interface import Interface
from zope.interface.verify import verifyClass
from zope.schema import Text, Int

from zope.component.service import serviceManager
from zope.app.interfaces.security import IPermissionService
from zope.app.security.registries.permissionregistry \
     import permissionRegistry
from zope.app.services.servicenames import Permissions
from zope.security.checker import CheckerPublic
from zope.security.management import newSecurityManager
from zope.security.management import system_user

from zope.proxy.context import ContextWrapper
from zope.app.traversing import traverse

from zope.app.container.zopecontainer import ZopeContainerAdapter

from zope.app.interfaces.services.configuration \
     import IUseConfigurable
from zope.app.interfaces.annotation import IAttributeAnnotatable
from zope.app.interfaces.services.configuration \
     import Active, Unregistered, Registered

from zope.app.workflow.tests.workflowsetup import WorkflowSetup
from zope.app.workflow.service import WorkflowService
from zope.app.workflow.service import ProcessDefinitionConfiguration
from zope.app.interfaces.workflow.stateful \
     import IStatefulProcessInstance
from zope.app.workflow.stateful.definition \
     import StatefulProcessDefinition, State, Transition
from zope.app.workflow.stateful.instance \
     import StatefulProcessInstance, StateChangeInfo




# define and create ProcessDefinition (PD) for tests
class TestProcessDefinition(StatefulProcessDefinition):
    __implements__ = IAttributeAnnotatable, IUseConfigurable, \
                     StatefulProcessDefinition.__implements__



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

        pd.states.setObject('private', State())
        pd.states.setObject('published', State())
        pd.states.setObject('pending', State())
        
        pd.transitions.setObject('show',
                                 Transition('INITIAL', 'private'))
        pd.transitions.setObject('publish_direct',
                                 Transition('private', 'published'))
        pd.transitions.setObject('publish_pending',
                                 Transition('pending', 'published'))
        pd.transitions.setObject('submit_pending',
                                 Transition('private', 'pending'))
        pd.transitions.setObject('retract_published',
                                 Transition('published', 'private'))
        pd.transitions.setObject('retract_pending',
                                 Transition('pending', 'private'))

        self.default.setObject('pd1', pd )

        self.cm.setObject('', ProcessDefinitionConfiguration('definition1',
                                '/++etc++site/default/pd1'))
        traverse(self.default.getConfigurationManager(), '2').status = Active

        self.pd = self.service.getProcessDefinition('definition1')
        # give the pi some context to find a service
        self.pi = ContextWrapper(self.service.createProcessInstance('definition1'),
                                 self.rootFolder)


    def testInterface(self):
        verifyClass(IStatefulProcessInstance, StatefulProcessInstance)


    def testRelevantData(self):
        pi = self.pi
        data = pi.data

        self.assert_(ITestDataSchema.isImplementedBy(data))

        self.assertEqual(data.text, 'no text')
        self.assertEqual(data.value, 1)

        data.text = 'another text'
        data.value = 10

        self.assertEqual(data.text, 'another text')
        self.assertEqual(data.value, 10)
        

    def testSimpleTranstitions(self):
        pi = self.pi
        pd = self.pd
        
        self.assertEqual(pi.status, pd.getInitialStateName())
        self.assertEqual(pi.getOutgoingTransitions(), ['show'])
        
        pi.fireTransition('show')
        self.assertEqual(pi.status, 'private')
        self.assertEqual(sort(pi.getOutgoingTransitions()),
                         ['publish_direct', 'submit_pending'])

        pi.fireTransition('submit_pending')
        self.assertEqual(pi.status, 'pending')
        self.assertEqual(sort(pi.getOutgoingTransitions()),
                         ['publish_pending', 'retract_pending'])

        pi.fireTransition('publish_pending')
        self.assertEqual(pi.status, 'published')
        self.assertEqual(sort(pi.getOutgoingTransitions()),
                         ['retract_published'])

        pi.fireTransition('retract_published')
        self.assertEqual(pi.status, 'private')

        pi.fireTransition('submit_pending')
        self.assertEqual(pi.status, 'pending')

        pi.fireTransition('retract_pending')
        self.assertEqual(pi.status, 'private')





class ConditionProcessInstanceTests(WorkflowSetup, unittest.TestCase):

    def setUp(self):
        WorkflowSetup.setUp(self)

        pd = TestProcessDefinition()

        pd.setRelevantDataSchema(ITestDataSchema)

        pd.states.setObject('state1', State())
        pd.states.setObject('state2', State())
        
        pd.transitions.setObject('initial_state1',
                                 Transition('INITIAL', 'state1',
                                            condition='data/value'))
        pd.transitions.setObject('initial_state2',
                                 Transition('INITIAL', 'state2',
                                            condition='not: data/value'))
        pd.transitions.setObject('state1_state2',
                                 Transition('state1', 'state2',
                                            condition='python: data.text == "some text"'))
        pd.transitions.setObject('state2_state1',
                                 Transition('state2', 'state1',
                                            condition='python: data.text == "no text"'))
        pd.transitions.setObject('state1_initial',
                                 Transition('state1', 'INITIAL'))
        pd.transitions.setObject('state2_initial',
                                 Transition('state2', 'INITIAL'))

        self.default.setObject('pd1', pd )

        self.cm.setObject('', ProcessDefinitionConfiguration('definition1',
                                '/++etc++site/default/pd1'))
        traverse(self.default.getConfigurationManager(), '2').status = Active

        self.pd = self.service.getProcessDefinition('definition1')
        # give the pi some context to find a service
        self.pi = ContextWrapper(self.service.createProcessInstance('definition1'),
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

        pd.states.setObject('state1', State())
        pd.states.setObject('state2', State())
        
        pd.transitions.setObject('initial_state1',
                                 Transition('INITIAL', 'state1',
                                            script=lambda c: c['data'].value))
        pd.transitions.setObject('initial_state2',
                                 Transition('INITIAL', 'state2',
                                            script=lambda c: not c['data'].value))
        pd.transitions.setObject('state1_state2',
                                 Transition('state1', 'state2',
                                            script=transition_script1))
        pd.transitions.setObject('state2_state1',
                                 Transition('state2', 'state1',
                                            script=transition_script2))
        pd.transitions.setObject('state1_initial',
                                 Transition('state1', 'INITIAL'))
        pd.transitions.setObject('state2_initial',
                                 Transition('state2', 'INITIAL'))

        self.default.setObject('pd1', pd )

        self.cm.setObject('', ProcessDefinitionConfiguration('definition1',
                                '/++etc++site/default/pd1'))
        traverse(self.default.getConfigurationManager(), '2').status = Active

        self.pd = self.service.getProcessDefinition('definition1')
        # give the pi some context to find a service
        self.pi = ContextWrapper(self.service.createProcessInstance('definition1'),
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

        pd.states.setObject('state1', State())
        pd.states.setObject('state2', State())
        
        pd.transitions.setObject('initial_state1',
                                 Transition('INITIAL', 'state1', permission=CheckerPublic))
        pd.transitions.setObject('initial_state2',
                                 Transition('INITIAL', 'state2', permission='deny'))
        pd.transitions.setObject('state1_state2',
                                 Transition('state1', 'state2', permission=CheckerPublic))
        pd.transitions.setObject('state2_state1',
                                 Transition('state2', 'state1'))
        pd.transitions.setObject('state1_initial',
                                 Transition('state1', 'INITIAL', permission='deny'))
        pd.transitions.setObject('state2_initial',
                                 Transition('state2', 'INITIAL', permission=CheckerPublic))

        self.default.setObject('pd1', pd )

        self.cm.setObject('', ProcessDefinitionConfiguration('definition1',
                                '/++etc++site/default/pd1'))
        traverse(self.default.getConfigurationManager(), '2').status = Active

        self.pd = self.service.getProcessDefinition('definition1')
        # give the pi some context to find a service
        self.pi = ContextWrapper(self.service.createProcessInstance('definition1'),
                                 self.rootFolder)



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
