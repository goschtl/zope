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
$Id: test_workflowservice.py,v 1.4 2003/03/13 18:49:12 alga Exp $
"""

import unittest
from zope.interface import Interface

class engineInterface(Interface):
    pass

class dummyEngine:
    __implements__ = engineInterface

    def listActions(self):
        return [0, 1, 2]

class WorkflowServiceTests(unittest.TestCase):

    def createService(self):
        from zope.app.workflow.workflowservice import WorkflowService
        service = WorkflowService()
        return service


    def testInterface(self):
        from zope.app.interfaces.workflow import IWorkflowService
        from zope.app.workflow.workflowservice import WorkflowService
        from zope.interface.verify import verifyClass

        verifyClass(IWorkflowService, WorkflowService)


    def testGetEngine(self):
        service = self.createService()
        self.assertEqual(service.getEngine(engineInterface), [])

    def testAddEngine(self):
        service = self.createService()
        engine = dummyEngine()
        service.addEngine(engine)
        self.assertEqual(service.getEngine(engineInterface), [engine])


    def testRemoveEngine(self):
        service = self.createService()
        engine = dummyEngine()
        service.addEngine(engine)
        service.removeEngine(engine)
        self.assertEqual(service.getEngine(engineInterface), [])


    def testListWorkflowEngineActions(self):
        service = self.createService()
        engine = dummyEngine()
        service.addEngine(engine)
        self.assertEqual(service.listWorkflowEngineActions(),
                         engine.listActions())


def test_suite():
    # DISABLED BECAUSE OUTDATED

    suite = unittest.TestSuite()
    #suite.addTest(
    #    unittest.defaultTestLoader.loadTestsFromTestCase(
    #        WorkflowServiceTests))
    return suite

if __name__ == '__main__':
    unittest.main()
