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
from zope.interface.verify import verifyClass

class WorkflowWorkitemTests(unittest.TestCase):
    def testInterface(self):
        from zope.app.interfaces.workflow import IWorkflowWorkitem
        from zope.app.workflow.workflowworkitem import WorkflowWorkitem

        verifyClass(IWorkflowWorkitem, WorkflowWorkitem)

    def _getOne(self, *args, **kw):
        from zope.app.workflow.workflowworkitem import WorkflowWorkitem
        return WorkflowWorkitem(*args, **kw)

    def testGetProcessInstance(self):
        from zope.app.workflow.workflowworkitem import WorkflowWorkitem

        pi = []
        wi = self._getOne(pi)
        npi = wi.getProcessInstance()
        self.assertEqual(pi, npi)

    def testEmpty(self):
        from zope.app.workflow.workflowworkitem import WorkflowWorkitem, INIT

        pi = []
        wi = self._getOne(pi)
        assignee = wi.getAssignee()
        state = wi.getState()
        self.assertEqual(assignee, None)
        self.assertEqual(state, INIT)

    def testAssignee(self):
        from zope.app.workflow.workflowworkitem import WorkflowWorkitem

        pi = []
        wi = self._getOne(pi)
        assignee = []
        wi.assign(assignee)
        nassignee = wi.getAssignee()
        self.assertEqual(assignee, nassignee)

    def testBegin(self):
        from zope.app.workflow.workflowworkitem import WorkflowWorkitem, \
             WorkflowWorkitemException, BEGUN

        pi = []
        wi = self._getOne(pi)
        wi.begin()
        state = wi.getState()
        self.assertEqual(state, BEGUN)
        self.assertRaises(WorkflowWorkitemException, wi.begin)

    def testComplete(self):
        from zope.app.workflow.workflowworkitem import WorkflowWorkitem, \
             WorkflowWorkitemException, COMPLETED

        pi = []
        wi = self._getOne(pi)
        self.assertRaises(WorkflowWorkitemException, wi.complete)
        self.assertRaises(WorkflowWorkitemException, wi.fail)
        wi.begin()
        wi.complete()
        state = wi.getState()
        self.assertEqual(state, COMPLETED)
        self.assertRaises(WorkflowWorkitemException, wi.begin)
        self.assertRaises(WorkflowWorkitemException, wi.complete)
        self.assertRaises(WorkflowWorkitemException, wi.fail)

    def testFail(self):
        from zope.app.workflow.workflowworkitem import WorkflowWorkitem, \
             WorkflowWorkitemException, FAILED

        pi = []
        wi = self._getOne(pi)
        self.assertRaises(WorkflowWorkitemException, wi.complete)
        self.assertRaises(WorkflowWorkitemException, wi.fail)
        wi.begin()
        wi.fail()
        state = wi.getState()
        self.assertEqual(state, FAILED)
        self.assertRaises(WorkflowWorkitemException, wi.begin)
        self.assertRaises(WorkflowWorkitemException, wi.complete)
        self.assertRaises(WorkflowWorkitemException, wi.fail)


def test_suite():

    suite = unittest.TestSuite()
    suite.addTest(
        unittest.defaultTestLoader.loadTestsFromTestCase(
            WorkflowWorkitemTests ) )
    return suite

if __name__ == '__main__':
    unittest.main()
