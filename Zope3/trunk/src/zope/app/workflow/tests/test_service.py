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
$Id: test_service.py,v 1.1 2003/05/08 17:27:20 jack-e Exp $
"""

import unittest

from zope.interface import Interface
from zope.interface.verify import verifyClass

from zope.app.traversing import traverse
from zope.app.container.zopecontainer import ZopeContainerAdapter
from zope.app.interfaces.annotation import IAttributeAnnotatable
from zope.app.interfaces.services.configuration \
     import IUseConfigurable

from zope.app.interfaces.services.configuration \
     import Active, Unregistered, Registered

from zope.app.workflow.tests.workflowsetup import WorkflowSetup
from zope.app.interfaces.workflow \
     import IWorkflowService, IProcessDefinition
from zope.app.workflow.service import WorkflowService
from zope.app.workflow.service import ProcessDefinitionConfiguration

# define and create dummy ProcessDefinition (PD) for tests
class DummyProcessDefinition:
    __implements__ = IProcessDefinition, IAttributeAnnotatable, IUseConfigurable

    def __init__(self, n):
        self.n = n

    def __str__(self):
        return'PD #%d' % self.n
    
    def createProcessInstance(self, definition_name):
        return 'PI #%d' % self.n


def sort(l):
    l = [str(d) for d in l]
    l.sort()
    return l

class WorkflowServiceTests(WorkflowSetup, unittest.TestCase):

    def setUp(self):
        WorkflowSetup.setUp(self)
        # setup ProcessDefinitions
        self.default.setObject('pd1', DummyProcessDefinition(1))
        self.default.setObject('pd2', DummyProcessDefinition(2))

        self.cm.setObject('', ProcessDefinitionConfiguration('definition1',
                                '/++etc++site/default/pd1'))
        traverse(self.default.getConfigurationManager(), '2').status = Active
        self.cm.setObject('', ProcessDefinitionConfiguration('definition2',
                                '/++etc++site/default/pd2'))
        traverse(self.default.getConfigurationManager(), '3').status = Active
        self.cm.setObject('', ProcessDefinitionConfiguration('definition3',
                                '/++etc++site/default/pd1'))
        traverse(self.default.getConfigurationManager(), '4').status = Registered
        # Now self.service has definition1 and definition2 available
        # and knows about definition3

        self.default1.setObject('pd3', DummyProcessDefinition(3))
        self.default1.setObject('pd4', DummyProcessDefinition(4))

        self.cm1.setObject('', ProcessDefinitionConfiguration('definition1',
                            '/folder1/++etc++site/default/pd3'))
        traverse(self.default1.getConfigurationManager(), '2').status = Active
        self.cm1.setObject('', ProcessDefinitionConfiguration('definition4',
                            '/folder1/++etc++site/default/pd4'))
        traverse(self.default1.getConfigurationManager(), '3').status = Active
        # Now self.service1 overrides definition1, adds new definition4 available,
        # and inherits definition2 from self.service

    def testInterface(self):
        verifyClass(IWorkflowService, WorkflowService)

    def testGetProcessDefiniton(self):
        self.assertEqual('PD #1', str(self.service.getProcessDefinition('definition1')))
        self.assertEqual('PD #2', str(self.service.getProcessDefinition('definition2')))
        self.assertRaises(KeyError, self.service.getProcessDefinition, 'definition3')
        self.assertRaises(KeyError, self.service.getProcessDefinition, 'definition4')
                          
        self.assertEqual('PD #3', str(self.service1.getProcessDefinition('definition1')))
        self.assertEqual('PD #2', str(self.service1.getProcessDefinition('definition2')))
        self.assertRaises(KeyError, self.service1.getProcessDefinition, 'definition3')
        self.assertEqual('PD #4', str(self.service1.getProcessDefinition('definition4')))
        self.assertRaises(KeyError, self.service1.getProcessDefinition, 'definition5')

    def testQueryProcessDefinition(self):
        self.assertEqual('PD #1', str(self.service.queryProcessDefinition('definition1')))
        self.assertEqual('PD #2', str(self.service.queryProcessDefinition('definition2')))
        self.assertEqual(None, self.service.queryProcessDefinition('definition3'))
        self.assertEqual('xx', self.service.queryProcessDefinition('definition3', 'xx'))
        self.assertEqual(None, self.service.queryProcessDefinition('definition4'))
        self.assertEqual('xx', self.service.queryProcessDefinition('definition4', 'xx'))

        self.assertEqual('PD #3', str(self.service1.queryProcessDefinition('definition1')))
        self.assertEqual('PD #2', str(self.service1.queryProcessDefinition('definition2')))
        self.assertEqual(None, self.service1.queryProcessDefinition('definition3'))
        self.assertEqual('xx', self.service1.queryProcessDefinition('definition3', 'xx'))
        self.assertEqual('PD #4', str(self.service1.queryProcessDefinition('definition4')))
        self.assertEqual(None, self.service1.queryProcessDefinition('definition5'))
        self.assertEqual('xx', self.service1.queryProcessDefinition('definition5', 'xx'))


    def testGetProcessDefinitonNames(self):
        self.assertEqual(['definition1', 'definition2'],
                         sort(self.service.getProcessDefinitionNames()))
        self.assertEqual(['definition1', 'definition2', 'definition4'],
                         sort(self.service1.getProcessDefinitionNames()))

    def testCreateProcessInstance(self):
        pi = self.service.createProcessInstance('definition1')
        self.assertEqual(pi, 'PI #1')

        pi = self.service1.createProcessInstance('definition4')
        self.assertEqual(pi, 'PI #4')

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(
        WorkflowServiceTests))
    return suite

if __name__ == '__main__':
    unittest.main()
