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
"""Workflow Service Tests

$Id: test_service.py,v 1.11 2004/03/13 18:01:25 srichter Exp $
"""
import unittest

from zope.app import zapi
from zope.interface import implements
from zope.interface.verify import verifyClass
from zope.app.container.contained import Contained
from zope.app.interfaces.annotation import IAttributeAnnotatable
from zope.app.utility.interfaces import ILocalUtility
from zope.app.registration.interfaces import RegisteredStatus, ActiveStatus
from zope.app.utility import UtilityRegistration

from zope.app.workflow.tests.workflowsetup import WorkflowSetup
from zope.app.workflow.interfaces import \
     IWorkflowService, IProcessDefinition
from zope.app.workflow.service import WorkflowService

# define and create dummy ProcessDefinition (PD) for tests
class DummyProcessDefinition(Contained):
    implements(IProcessDefinition, IAttributeAnnotatable, ILocalUtility)

    def __init__(self, n):
        self.n = n

    def __str__(self):
        return'PD #%d' % self.n

    def createProcessInstance(self, definition_name):
        return 'PI #%d' % self.n

    # Implements (incompletely) IRegistered to satisfy the promise that
    # it is IRegisterable.
    # Only the method addUsage is implemented.
    def addUsage(self, location):
        pass


def sort(l):
    l = [str(d) for d in l]
    l.sort()
    return l

class WorkflowServiceTests(WorkflowSetup, unittest.TestCase):

    def setUp(self):
        WorkflowSetup.setUp(self)
        # setup ProcessDefinitions
        self.default['pd1'] = DummyProcessDefinition(1)
        self.default['pd2'] = DummyProcessDefinition(2)

        n = self.cm.addRegistration(
            UtilityRegistration('definition1', IProcessDefinition,
                                '/++etc++site/default/pd1'))
        zapi.traverse(self.default.getRegistrationManager(),
                      n).status = ActiveStatus
        n = self.cm.addRegistration(
            UtilityRegistration('definition2', IProcessDefinition,
                                '/++etc++site/default/pd2'))
        zapi.traverse(self.default.getRegistrationManager(),
                      n).status = ActiveStatus
        n = self.cm.addRegistration(
            UtilityRegistration('definition3', IProcessDefinition,
                                '/++etc++site/default/pd2'))
        zapi.traverse(self.default.getRegistrationManager(),
                 n).status = RegisteredStatus

        # Now self.service has definition1 and definition2 available
        # and knows about definition3

        self.default1['pd3'] = DummyProcessDefinition(3)
        self.default1['pd4'] = DummyProcessDefinition(4)

        n = self.cm1.addRegistration(
            UtilityRegistration('definition1', IProcessDefinition,
                                '/folder1/++etc++site/default/pd3'))
        zapi.traverse(self.default1.getRegistrationManager(),
                      n).status = ActiveStatus
        n = self.cm1.addRegistration(
            UtilityRegistration('definition4', IProcessDefinition,
                                '/folder1/++etc++site/default/pd4'))
        zapi.traverse(self.default1.getRegistrationManager(),
                      n).status = ActiveStatus

        # Now self.service1 overrides definition1, adds new definition4
        # available, and inherits definition2 from self.service

    def testInterface(self):
        verifyClass(IWorkflowService, WorkflowService)

    def testGetProcessDefiniton(self):
        self.assertEqual(
            'PD #1', str(self.service.getProcessDefinition('definition1')))
        self.assertEqual(
            'PD #2', str(self.service.getProcessDefinition('definition2')))
        self.assertRaises(
            KeyError, self.service.getProcessDefinition, 'definition3')
        self.assertRaises(
            KeyError, self.service.getProcessDefinition, 'definition4')

        self.assertEqual(
            'PD #3', str(self.service1.getProcessDefinition('definition1')))
        self.assertEqual(
            'PD #2', str(self.service1.getProcessDefinition('definition2')))
        self.assertRaises(
            KeyError, self.service1.getProcessDefinition, 'definition3')
        self.assertEqual(
            'PD #4', str(self.service1.getProcessDefinition('definition4')))
        self.assertRaises(
            KeyError, self.service1.getProcessDefinition, 'definition5')

    def testQueryProcessDefinition(self):
        self.assertEqual(
            'PD #1', str(self.service.queryProcessDefinition('definition1')))
        self.assertEqual(
            'PD #2', str(self.service.queryProcessDefinition('definition2')))
        self.assertEqual(
            None, self.service.queryProcessDefinition('definition3'))
        self.assertEqual(
            'xx', self.service.queryProcessDefinition('definition3', 'xx'))
        self.assertEqual(
            None, self.service.queryProcessDefinition('definition4'))
        self.assertEqual(
            'xx', self.service.queryProcessDefinition('definition4', 'xx'))

        self.assertEqual(
            'PD #3', str(self.service1.queryProcessDefinition('definition1')))
        self.assertEqual(
            'PD #2', str(self.service1.queryProcessDefinition('definition2')))
        self.assertEqual(
            None, self.service1.queryProcessDefinition('definition3'))
        self.assertEqual(
            'xx', self.service1.queryProcessDefinition('definition3', 'xx'))
        self.assertEqual(
            'PD #4', str(self.service1.queryProcessDefinition('definition4')))
        self.assertEqual(
            None, self.service1.queryProcessDefinition('definition5'))
        self.assertEqual(
            'xx', self.service1.queryProcessDefinition('definition5', 'xx'))


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
