##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Stateful content workflow manager.

$Id$
"""
import unittest

from zope.interface import Interface, implements
from zope.interface.verify import verifyClass

from zope.app import zapi
from zope.app.annotation.interfaces import IAttributeAnnotatable
from zope.app.container.contained import Contained
from zope.app.event.objectevent import ObjectCreatedEvent
from zope.app.annotation.interfaces import IAnnotatable, IAttributeAnnotatable
from zope.app.event.interfaces import IObjectCreatedEvent
from zope.app.component.site import UtilityRegistration
from zope.app.component.interfaces import ILocalUtility
from zope.app.component.interfaces.registration import ActiveStatus

from zope.app.workflow.interfaces import IProcessDefinition
from zope.app.workflow.interfaces import IProcessInstanceContainerAdaptable
from zope.app.workflow.interfaces import IProcessInstanceContainer
from zope.app.workflow.stateful.interfaces import IContentWorkflowsManager
from zope.app.workflow.instance import ProcessInstanceContainerAdapter
from zope.app.workflow.stateful.contentworkflow import ContentWorkflowsManager
from zope.app.workflow.stateful.contentworkflow \
     import NewObjectProcessInstanceCreator
from zope.app.workflow.tests.workflowsetup import WorkflowSetup

from zope.app.testing import ztapi, setup

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

class IFace1(Interface):
    pass

class IFace2(Interface):
    pass

class IFace3(Interface):
    pass

class TestObject1(object):
    implements(IFace1, IProcessInstanceContainerAdaptable,
               IAttributeAnnotatable)

class TestObject2(object):
    implements(IFace2, IProcessInstanceContainerAdaptable,
               IAttributeAnnotatable)

class TestObject3(object):
    implements(IFace3, IProcessInstanceContainerAdaptable,
               IAttributeAnnotatable)


class ContentWorkflowsManagerTest(WorkflowSetup, unittest.TestCase):

    def setUp(self):
        WorkflowSetup.setUp(self)
        ztapi.provideAdapter(IAnnotatable, IProcessInstanceContainer,
                             ProcessInstanceContainerAdapter)

    def testInterface(self):
        verifyClass(IContentWorkflowsManager, ContentWorkflowsManager)

    def getManager(self):
        manager = ContentWorkflowsManager()
        manager._registry = {IFace1: ('default',), IFace2: ('default',)}
        self.default['manager'] = manager
        return zapi.traverse(self.default, 'manager')

    def test_getProcessDefinitionNamesForObject(self):
        manager = self.getManager()
        self.assertEqual(
            manager.getProcessDefinitionNamesForObject(TestObject1()),
            ('default',))
        self.assertEqual(
            manager.getProcessDefinitionNamesForObject(TestObject2()),
            ('default',))
        self.assertEqual(
            manager.getProcessDefinitionNamesForObject(TestObject3()),
            ())

    def test_register(self):
        manager = self.getManager()
        manager._registry = {}
        manager.register(IFace1, 'default')
        self.assertEqual(manager._registry, {IFace1: ('default',)})

    def test_unregister(self):
        manager = self.getManager()
        manager.unregister(IFace1, 'default')
        self.assertEqual(manager._registry, {IFace2: ('default',)})

    def test_getProcessNamesForInterface(self):
        manager = self.getManager()
        self.assertEqual(
            manager.getProcessNamesForInterface(IFace1),
            ('default',))
        self.assertEqual(
            manager.getProcessNamesForInterface(IFace2),
            ('default',))
        self.assertEqual(
            manager.getProcessNamesForInterface(IFace3),
            ())

    def test_getInterfacesForProcessName(self):
        manager = self.getManager()
        ifaces = manager.getInterfacesForProcessName(u'default')
        self.assertEqual(len(ifaces), 2)
        for iface in [IFace1, IFace2]:
            self.failUnless(iface in ifaces)
        self.assertEqual(
            manager.getInterfacesForProcessName(u'foo'), ())

    def test_notify(self):
        # setup ProcessDefinitions

        setup.addUtility(self.sm, 'definition1', IProcessDefinition,
                         DummyProcessDefinition(1))
        setup.addUtility(self.sm, 'definition2', IProcessDefinition,
                         DummyProcessDefinition(2))

        manager = self.getManager()
        manager._registry = {IFace1: ('definition1',),
                             IFace2: ('definition1', 'definition2')}
        setup.addUtility(self.sm, '', IContentWorkflowsManager,
                         manager)

        obj = TestObject2()
        event = ObjectCreatedEvent(obj)
        NewObjectProcessInstanceCreator(obj, event)
        pi = obj.__annotations__['zope.app.worfklow.ProcessInstanceContainer']
        self.assertEqual(pi.keys(), ['definition2', 'definition1'])


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(ContentWorkflowsManagerTest),
        ))

if __name__ == '__main__':
    unittest.main()
