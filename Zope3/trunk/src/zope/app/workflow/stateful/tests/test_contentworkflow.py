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
from zope.app.event.tests.placelesssetup import eventPublisher, EventRecorder
from zope.app.event.tests.placelesssetup import clearEvents
from zope.app.annotation.interfaces import IAnnotatable, IAttributeAnnotatable
from zope.app.event.interfaces import IObjectCreatedEvent, ISubscriptionService
from zope.app.event.localservice import EventService
from zope.app.servicenames import EventSubscription
from zope.app.utility import UtilityRegistration
from zope.app.utility.interfaces import ILocalUtility
from zope.app.registration.interfaces import ActiveStatus

from zope.app.workflow.interfaces import IProcessDefinition
from zope.app.workflow.interfaces import IProcessInstanceContainerAdaptable
from zope.app.workflow.interfaces import IProcessInstanceContainer
from zope.app.workflow.stateful.interfaces import IContentWorkflowsManager
from zope.app.workflow.instance import ProcessInstanceContainerAdapter
from zope.app.workflow.stateful.contentworkflow import ContentWorkflowsManager
from zope.app.workflow.tests.workflowsetup import WorkflowSetup

from zope.app.tests import ztapi, setup

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
        sm = zapi.getGlobalServices()
        sm.defineService(EventSubscription, ISubscriptionService)
        self.events = EventService()
        setup.addService(self.sm, EventSubscription, self.events)
        clearEvents()
        eventPublisher.globalSubscribe(EventRecorder)
        ztapi.provideAdapter(IAnnotatable, IProcessInstanceContainer,
                             ProcessInstanceContainerAdapter)

    def testInterface(self):
        verifyClass(IContentWorkflowsManager, ContentWorkflowsManager)

    def getManager(self):
        manager = ContentWorkflowsManager()
        manager._registry = {IFace1: ('default',), IFace2: ('default',)}
        self.default['manager'] = manager
        return zapi.traverse(self.default, 'manager')

    def test_subscribe(self):
        manager = self.getManager()
        self.assertEqual(manager.currentlySubscribed, False)
        manager.subscribe()
        self.assertEqual(manager.currentlySubscribed, True)
        self.assertEqual(self.events._registry._reg.keys()[0],
                         IObjectCreatedEvent)
        self.assertEqual(self.events._registry._reg.values()[0][0][0],
                         u'/++etc++site/default/manager')

    def test_unsubscribe(self):
        manager = self.getManager()
        self.assertEqual(manager.currentlySubscribed, False)
        manager.subscribe()
        manager.unsubscribe()
        self.assertEqual(manager.currentlySubscribed, False)
        self.assertEqual(len(self.events._registry._reg.values()), 0)

    def test_isSubscribed(self):
        manager = self.getManager()
        self.assertEqual(manager.isSubscribed(), False)
        manager.subscribe()
        self.assertEqual(manager.isSubscribed(), True)
        manager.unsubscribe()
        self.assertEqual(manager.isSubscribed(), False)

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
        self.default['pd1'] = DummyProcessDefinition(1)
        self.default['pd2'] = DummyProcessDefinition(2)

        id = self.cm.addRegistration(
            UtilityRegistration('definition1', IProcessDefinition,
                                '/++etc++site/default/pd1'))
        zapi.traverse(self.default.getRegistrationManager(),
                      id).status = ActiveStatus
        id = self.cm.addRegistration(
            UtilityRegistration('definition2', IProcessDefinition,
                                '/++etc++site/default/pd2'))
        zapi.traverse(self.default.getRegistrationManager(),
                      id).status = ActiveStatus
        manager = self.getManager()
        manager._registry = {IFace1: ('definition1',),
                             IFace2: ('definition1', 'definition2')}

        obj = TestObject2()
        manager.notify(ObjectCreatedEvent(obj))
        pi = obj.__annotations__['zope.app.worfklow.ProcessInstanceContainer']
        self.assertEqual(pi.keys(), ['definition2', 'definition1'])


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(ContentWorkflowsManagerTest),
        ))

if __name__ == '__main__':
    unittest.main()
