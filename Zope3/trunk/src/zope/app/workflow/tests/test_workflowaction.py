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
import unittest

class WorkflowActionTestsBase:

    def test_getAction( self ):
        ACTION = []
        event = self._makeOne( ACTION )
        self.assertEqual( event.getAction(), ACTION )

    def _makeOne( self, *args, **kw ):

        return self._getEventClass()( *args, **kw )

class WorkflowActionCreatedTests( unittest.TestCase, WorkflowActionTestsBase ):

    def testInterface( self ):
        from zope.app.interfaces.workflow import IWorkflowEvent
        from zope.app.interfaces.workflow import IWorkflowActionEvent
        from zope.app.interfaces.workflow \
            import IWorkflowActionCreatedEvent
        from zope.app.workflow.workflowevents import WorkflowActionCreatedEvent
        from zope.interface.verify import verifyClass

        verifyClass( IWorkflowEvent, WorkflowActionCreatedEvent )
        verifyClass( IWorkflowActionEvent, WorkflowActionCreatedEvent )
        verifyClass( IWorkflowActionCreatedEvent, WorkflowActionCreatedEvent )

    def _getEventClass( self ):
        from zope.app.workflow.workflowevents import WorkflowActionCreatedEvent
        return WorkflowActionCreatedEvent


class WorkflowActionAssignedEventTest( unittest.TestCase
                                     , WorkflowActionTestsBase ):

    def testInterface( self ):
        from zope.app.interfaces.workflow import IWorkflowEvent
        from zope.app.interfaces.workflow import IWorkflowActionEvent
        from zope.app.interfaces.workflow \
            import IWorkflowActionAssignedEvent
        from zope.app.workflow.workflowevents \
            import WorkflowActionAssignedEvent
        from zope.interface.verify import verifyClass

        verifyClass( IWorkflowEvent, WorkflowActionAssignedEvent )
        verifyClass( IWorkflowActionEvent, WorkflowActionAssignedEvent )
        verifyClass( IWorkflowActionAssignedEvent, WorkflowActionAssignedEvent )

    def _getEventClass( self ):
        from zope.app.workflow.workflowevents import WorkflowActionAssignedEvent
        return WorkflowActionAssignedEvent


class WorkflowActionBegunEventTest( unittest.TestCase, WorkflowActionTestsBase ):

    def testInterface( self ):
        from zope.app.interfaces.workflow import IWorkflowEvent
        from zope.app.interfaces.workflow import IWorkflowActionEvent
        from zope.app.interfaces.workflow import IWorkflowActionBegunEvent
        from zope.app.workflow.workflowevents import WorkflowActionBegunEvent
        from zope.interface.verify import verifyClass

        verifyClass( IWorkflowEvent, WorkflowActionBegunEvent )
        verifyClass( IWorkflowActionEvent, WorkflowActionBegunEvent )
        verifyClass( IWorkflowActionBegunEvent, WorkflowActionBegunEvent )

    def _getEventClass( self ):
        from zope.app.workflow.workflowevents import WorkflowActionBegunEvent
        return WorkflowActionBegunEvent


class WorkflowActionSuspendedTests( unittest.TestCase, WorkflowActionTestsBase ):

    def testInterface(self):
        from zope.app.interfaces.workflow import IWorkflowEvent
        from zope.app.interfaces.workflow import IWorkflowActionEvent
        from zope.app.interfaces.workflow \
             import IWorkflowActionSuspendedEvent
        from zope.app.workflow.workflowevents \
             import WorkflowActionSuspendedEvent
        from zope.interface.verify import verifyClass

        verifyClass( IWorkflowEvent, WorkflowActionSuspendedEvent )
        verifyClass( IWorkflowActionEvent, WorkflowActionSuspendedEvent )
        verifyClass( IWorkflowActionSuspendedEvent, WorkflowActionSuspendedEvent )

    def _getEventClass( self ):
        from zope.app.workflow.workflowevents \
            import WorkflowActionSuspendedEvent
        return WorkflowActionSuspendedEvent


class WorkflowActionCompletedEvent(unittest.TestCase, WorkflowActionTestsBase):

    def testInterface(self):
        from zope.app.interfaces.workflow import IWorkflowEvent
        from zope.app.interfaces.workflow import IWorkflowActionEvent
        from zope.app.interfaces.workflow \
            import IWorkflowActionCompletedEvent
        from zope.app.workflow.workflowevents \
            import WorkflowActionCompletedEvent
        from zope.interface.verify import verifyClass

        verifyClass(IWorkflowEvent, WorkflowActionCompletedEvent)
        verifyClass(IWorkflowActionEvent, WorkflowActionCompletedEvent)
        verifyClass(IWorkflowActionCompletedEvent, WorkflowActionCompletedEvent)

    def _getEventClass( self ):
        from zope.app.workflow.workflowevents \
            import WorkflowActionCompletedEvent
        return WorkflowActionCompletedEvent


class WorkflowActionExceptionEvent(unittest.TestCase, WorkflowActionTestsBase):

    def testInterface(self):
        from zope.app.interfaces.workflow import IWorkflowEvent
        from zope.app.interfaces.workflow import IWorkflowActionEvent
        from zope.app.interfaces.workflow \
            import IWorkflowActionExceptionEvent
        from zope.app.workflow.workflowevents \
            import WorkflowActionExceptionEvent
        from zope.interface.verify import verifyClass

        verifyClass(IWorkflowEvent, WorkflowActionExceptionEvent)
        verifyClass(IWorkflowActionEvent, WorkflowActionExceptionEvent)
        verifyClass(IWorkflowActionExceptionEvent, WorkflowActionExceptionEvent)

    def _getEventClass( self ):
        from zope.app.workflow.workflowevents \
            import WorkflowActionExceptionEvent
        return WorkflowActionExceptionEvent

    def _getEventClass( self ):
        from zope.app.workflow.workflowevents \
            import WorkflowActionExceptionEvent
        return WorkflowActionExceptionEvent


def test_suite():

    suite = unittest.TestSuite()
    for klass in ( WorkflowActionCreatedTests
                 , WorkflowActionAssignedEventTest
                 , WorkflowActionBegunEventTest
                 , WorkflowActionSuspendedTests
                 , WorkflowActionCompletedEvent
                 , WorkflowActionExceptionEvent
                 ):
        suite.addTest(
            unittest.defaultTestLoader.loadTestsFromTestCase( klass ) )
    return suite


if __name__ == '__main__':
    unittest.main()
