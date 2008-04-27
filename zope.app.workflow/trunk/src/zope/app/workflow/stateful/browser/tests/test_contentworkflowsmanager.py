##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Functional Tests for ContentWorkflowsManager

$Id$
"""
import unittest
import re

from transaction import commit
from zope.interface import Interface
from zope.component.interface import nameToInterface
from zope.traversing.api import traverse

from zope.app.testing.functional import BrowserTestCase
from zope.app.testing.setup import addUtility

from zope.app.workflow.stateful.definition import StatefulProcessDefinition
from zope.app.workflow.stateful.interfaces import IStatefulProcessDefinition,\
     IContentWorkflowsManager
from zope.app.workflow.testing import AppWorkflowLayer

class Test(BrowserTestCase):

    def setUp(self):
        super(Test, self).setUp()
        self.basepath = '/++etc++site/default'
        root = self.getRootFolder()

        sm = traverse(root, '/++etc++site')
        addUtility(sm,
                   'dummy-definition',
                   IStatefulProcessDefinition,
                   StatefulProcessDefinition()
                   )
        commit()

        response = self.publish(
            self.basepath + '/contents.html',
            basic='mgr:mgrpw',
            form={'type_name':
                  'BrowserAdd__'
                  'zope.app.workflow.stateful.contentworkflow.'
                  'ContentWorkflowsManager',
                  'new_value': 'mgr' })

        sm.registerUtility(sm['default']['mgr'],
                           IContentWorkflowsManager, 'cwm')

    def test_registry(self):
        response = self.publish(
            self.basepath + '/mgr/index.html',
            basic='mgr:mgrpw')

        self.assertEqual(response.getStatus(), 200)
        body = ' '.join(response.getBody().split())
        self.assert_(body.find(
            '<option value="zope.app.folder.interfaces.IFolder">'
            ) >= 0)
        self.assert_(body.find(
            '<option value="zope.app.file.interfaces.IFile">'
            ) >= 0)

        response = self.publish(
            self.basepath + '/mgr/index.html',
            basic='mgr:mgrpw',
            form={
            'field.iface':['zope.app.folder.interfaces.IFolder',
                           'zope.app.file.interfaces.IFile'],
            'field.name':['dummy-definition'],
            'ADD':'Add'
            })

        self.assertEqual(response.getStatus(), 200)
        root = self.getRootFolder()
        mgr = traverse(root, self.basepath+'/mgr')
        ifaces = mgr.getInterfacesForProcessName('dummy-definition')

        self.assert_(nameToInterface(
            None,
            'zope.app.folder.interfaces.IFolder'
            ) in ifaces)
        self.assert_(nameToInterface(
            None,
            'zope.app.file.interfaces.IFile'
            ) in ifaces)
        self.assertEqual(len(ifaces), 2)

        response = self.publish(
            self.basepath + '/mgr/index.html',
            basic='mgr:mgrpw',
            form={
            'mappings': ['dummy-definition:zope.app.folder.interfaces.IFolder',
                         'dummy-definition:zope.app.file.interfaces.IFile'],
            'REMOVE':''
            })

        ifaces = mgr.getInterfacesForProcessName('dummy-definition')
        self.assertEqual(len(ifaces), 0)

def test_suite():
    Test.layer = AppWorkflowLayer
    return unittest.makeSuite(Test)

if __name__ == '__main__':
    unittest.main()
