##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Functional Tests for StatefulProcessDefinition

$Id$
"""
import unittest
import re

from zope.app import zapi
from zope.app.tests.functional import BrowserTestCase
from zope.app.workflow.stateful.definition import StatefulProcessDefinition

class Test(BrowserTestCase):

    def setUp(self):
        super(Test, self).setUp()
        self.basepath = '/++etc++site/default'
        response = self.publish(
            self.basepath + '/contents.html',
            basic='mgr:mgrpw')

        self.assertEqual(response.getStatus(), 200)

        expr = 'zope.app.browser.add.StatefulProcessDefinition.f([0-9]*)'
        m = re.search(expr, response.getBody())
        type_name = m.group(0)

        response = self.publish(
            self.basepath + '/contents.html',
            basic='mgr:mgrpw',
            form={'type_name': type_name,
                  'new_value': 'pd' })

    def test_processdefinition(self):
        response = self.publish(
            self.basepath + '/pd/index.html',
            basic='mgr:mgrpw')

        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assert_(body.find("I'm a stateful ProcessInstance") >= 0)

        response = self.publish(
            self.basepath + '/pd/edit.html',
            basic='mgr:mgrpw')

        self.assertEqual(response.getStatus(), 200)
        body = ' '.join(response.getBody().split())
        self.assert_(body.find('Set Workflow-Relevant Data Schema') >= 0)

        response = self.publish(
            self.basepath + '/pd/registration.html',
            basic='mgr:mgrpw')

        self.assertEqual(response.getStatus(), 200)
        body = ' '.join(response.getBody().split())
        self.assert_(body.find('This object is not currently active.') >=0)

        response = self.publish(
            self.basepath + '/pd/importexport.html',
            basic='mgr:mgrpw')

        self.assertEqual(response.getStatus(), 200)
        body = ' '.join(response.getBody().split())
        self.assert_(body.find('Import / Export Process Definitions:') >= 0)
        self.assert_(body.find(
            '<a href="states/contents.html">Manage States</a>') >=0 )
        self.assert_(body.find(
            '<a href="transitions/contents.html">Manage Transitions</a>') >=0)

    def test_transitions(self):
        response = self.publish(
            self.basepath + '/pd/transitions/contents.html',
            basic='mgr:mgrpw')

        self.assertEqual(response.getStatus(), 200)

    def test_states(self):
        response = self.publish(
            self.basepath + '/pd/states/contents.html',
            basic='mgr:mgrpw')

        self.assertEqual(response.getStatus(), 200)
        body = ' '.join(response.getBody().split())
        self.assert_(body.find('INITIAL') >= 0)


def test_suite():
    return unittest.makeSuite(Test)

if __name__ == '__main__':
    unittest.main()
