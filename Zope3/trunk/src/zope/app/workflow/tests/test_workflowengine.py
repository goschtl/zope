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


class WorkflowEngineTests( unittest.TestCase ):

    def testInterface( self ):
        from zope.app.interfaces.workflow import IWorkflowEngine
        from zope.app.workflow.workflowengine import WorkflowEngine
        from zope.interface.verify import verifyClass

        verifyClass( IWorkflowEngine, WorkflowEngine )



def test_suite():
    # DISABLED BECAUSE OUTDATED

    suite = unittest.TestSuite()
    #suite.addTest(
    #    unittest.defaultTestLoader.loadTestsFromTestCase(
    #        WorkflowEngineTests ) )
    return suite



if __name__ == '__main__':
    unittest.main()
