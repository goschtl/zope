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
        from Zope.App.Workflow.IWorkflowEvents import IWorkflowEvent
        from Zope.App.Workflow.IWorkflowEvents import IWorkflowActionEvent
        from Zope.App.Workflow.IWorkflowEvents \
            import IWorkflowActionCreatedEvent
        from Zope.App.Workflow.WorkflowEvents import WorkflowActionCreatedEvent
        from Interface.Verify import verifyClass

        verifyClass( IWorkflowEvent, WorkflowActionCreatedEvent )
        verifyClass( IWorkflowActionEvent, WorkflowActionCreatedEvent )
        verifyClass( IWorkflowActionCreatedEvent, WorkflowActionCreatedEvent )

    def _getEventClass( self ):
        from Zope.App.Workflow.WorkflowEvents import WorkflowActionCreatedEvent
        return WorkflowActionCreatedEvent


class WorkflowActionAssignedEventTest( unittest.TestCase
                                     , WorkflowActionTestsBase ):

    def testInterface( self ):
        from Zope.App.Workflow.IWorkflowEvents import IWorkflowEvent
        from Zope.App.Workflow.IWorkflowEvents import IWorkflowActionEvent
        from Zope.App.Workflow.IWorkflowEvents \
            import IWorkflowActionAssignedEvent
        from Zope.App.Workflow.WorkflowEvents \
            import WorkflowActionAssignedEvent
        from Interface.Verify import verifyClass
        
        verifyClass( IWorkflowEvent, WorkflowActionAssignedEvent )
        verifyClass( IWorkflowActionEvent, WorkflowActionAssignedEvent )
        verifyClass( IWorkflowActionAssignedEvent, WorkflowActionAssignedEvent )

    def _getEventClass( self ):
        from Zope.App.Workflow.WorkflowEvents import WorkflowActionAssignedEvent
        return WorkflowActionAssignedEvent


class WorkflowActionBegunEventTest( unittest.TestCase, WorkflowActionTestsBase ):

    def testInterface( self ):
        from Zope.App.Workflow.IWorkflowEvents import IWorkflowEvent
        from Zope.App.Workflow.IWorkflowEvents import IWorkflowActionEvent
        from Zope.App.Workflow.IWorkflowEvents import IWorkflowActionBegunEvent
        from Zope.App.Workflow.WorkflowEvents import WorkflowActionBegunEvent
        from Interface.Verify import verifyClass
        
        verifyClass( IWorkflowEvent, WorkflowActionBegunEvent )
        verifyClass( IWorkflowActionEvent, WorkflowActionBegunEvent )
        verifyClass( IWorkflowActionBegunEvent, WorkflowActionBegunEvent )

    def _getEventClass( self ):
        from Zope.App.Workflow.WorkflowEvents import WorkflowActionBegunEvent
        return WorkflowActionBegunEvent


class WorkflowActionSuspendedTests( unittest.TestCase, WorkflowActionTestsBase ):

    def testInterface(self):
        from Zope.App.Workflow.IWorkflowEvents import IWorkflowEvent
        from Zope.App.Workflow.IWorkflowEvents import IWorkflowActionEvent
        from Zope.App.Workflow.IWorkflowEvents \
             import IWorkflowActionSuspendedEvent
        from Zope.App.Workflow.WorkflowEvents \
             import WorkflowActionSuspendedEvent
        from Interface.Verify import verifyClass

        verifyClass( IWorkflowEvent, WorkflowActionSuspendedEvent )
        verifyClass( IWorkflowActionEvent, WorkflowActionSuspendedEvent )
        verifyClass( IWorkflowActionSuspendedEvent, WorkflowActionSuspendedEvent )

    def _getEventClass( self ):
        from Zope.App.Workflow.WorkflowEvents \
            import WorkflowActionSuspendedEvent
        return WorkflowActionSuspendedEvent


class WorkflowActionCompletedEvent(unittest.TestCase, WorkflowActionTestsBase):

    def testInterface(self):
        from Zope.App.Workflow.IWorkflowEvents import IWorkflowEvent
        from Zope.App.Workflow.IWorkflowEvents import IWorkflowActionEvent
        from Zope.App.Workflow.IWorkflowEvents \
            import IWorkflowActionCompletedEvent
        from Zope.App.Workflow.WorkflowEvents \
            import WorkflowActionCompletedEvent
        from Interface.Verify import verifyClass

        verifyClass(IWorkflowEvent, WorkflowActionCompletedEvent)
        verifyClass(IWorkflowActionEvent, WorkflowActionCompletedEvent)
        verifyClass(IWorkflowActionCompletedEvent, WorkflowActionCompletedEvent)

    def _getEventClass( self ):
        from Zope.App.Workflow.WorkflowEvents \
            import WorkflowActionCompletedEvent
        return WorkflowActionCompletedEvent


class WorkflowActionExceptionEvent(unittest.TestCase, WorkflowActionTestsBase):

    def testInterface(self):
        from Zope.App.Workflow.IWorkflowEvents import IWorkflowEvent
        from Zope.App.Workflow.IWorkflowEvents import IWorkflowActionEvent
        from Zope.App.Workflow.IWorkflowEvents \
            import IWorkflowActionExceptionEvent
        from Zope.App.Workflow.WorkflowEvents \
            import WorkflowActionExceptionEvent
        from Interface.Verify import verifyClass

        verifyClass(IWorkflowEvent, WorkflowActionExceptionEvent)
        verifyClass(IWorkflowActionEvent, WorkflowActionExceptionEvent)
        verifyClass(IWorkflowActionExceptionEvent, WorkflowActionExceptionEvent)

    def _getEventClass( self ):
        from Zope.App.Workflow.WorkflowEvents \
            import WorkflowActionExceptionEvent
        return WorkflowActionExceptionEvent

    def _getEventClass( self ):
        from Zope.App.Workflow.WorkflowEvents \
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
