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
from Interface.Verify import verifyClass

class WorkflowActivityInfoTests(unittest.TestCase):

    def testInterface(self):
        from Zope.App.Workflow.IWorkflowActivityInfo \
            import IWorkflowActivityInfo
        from Zope.App.Workflow.WorkflowActivityInfo \
            import WorkflowActivityInfo

        verifyClass(IWorkflowActivityInfo, WorkflowActivityInfo)

    def _getOne(self, *args, **kw):
        from Zope.App.Workflow.WorkflowActivityInfo import WorkflowActivityInfo
        return WorkflowActivityInfo(*args, **kw)

    def testEmpty(self):
        id = 'blah'
        ai = self._getOne(id)
        self.assertEqual(ai.getId(), id)
        self.assertEqual(ai.getTitle(), '')
        self.assertEqual(ai.getCategory(), '')
        self.assertEqual(ai.getActionURL(), '')
        self.assertEqual(len(ai.getPermissions()), 0)
        self.assertEqual(len(ai.getRoles()), 0)
        self.assertEqual(ai.getCondition(), None)
        self.assertEqual(ai.getSource(), None)

    def testTitle(self):
        id = 'blah'
        title = 'zoinx'
        ai = self._getOne(id, title=title)
        self.assertEqual(ai.getTitle(), title)

    def testCategory(self):
        id = 'blah'
        category = 'foobar'
        ai = self._getOne(id, category=category)
        self.assertEqual(ai.getCategory(), category)

    def testActionURL(self):
        id = 'blah'
        action_url = 'baz'
        ai = self._getOne(id, action_url=action_url)
        self.assertEqual(ai.getActionURL(), action_url)

    def testPermissions(self):
        id = 'blah'
        permissions = [1,2,3]
        ai = self._getOne(id, permissions=permissions)
        self.assertEqual(ai.getPermissions(), permissions)

    def testRoles(self):
        id = 'blah'
        roles = [4,5,6]
        ai = self._getOne(id, roles=roles)
        self.assertEqual(ai.getRoles(), roles)

    def testCondition(self):
        id = 'blah'
        condition = []
        ai = self._getOne(id, condition=condition)
        self.assertEqual(ai.getCondition(), condition)

    def testSource(self):
        id = 'blah'
        source = []
        ai = self._getOne(id, source=source)
        self.assertEqual(ai.getSource(), source)

    def testComplex(self):
        id = 'blah'
        title = 'zoinx'
        category = 'foobar'
        action_url = 'baz'
        permissions = [1,2,3]
        roles = [4,5,6]
        condition = []
        source = []
        ai = self._getOne(id, title=title, category=category,
                          action_url=action_url, permissions=permissions,
                          roles=roles, condition=condition,
                          source=source)
        self.assertEqual(ai.getId(), id)
        self.assertEqual(ai.getTitle(), title)
        self.assertEqual(ai.getCategory(), category)
        self.assertEqual(ai.getActionURL(), action_url)
        self.assertEqual(ai.getPermissions(), permissions)
        self.assertEqual(ai.getRoles(), roles)
        self.assertEqual(ai.getCondition(), condition)
        self.assertEqual(ai.getSource(), source)

def test_suite():

    suite = unittest.TestSuite()
    suite.addTest(
        unittest.defaultTestLoader.loadTestsFromTestCase(
            WorkflowActivityInfoTests ) )
    return suite

if __name__ == '__main__':
    unittest.main()
