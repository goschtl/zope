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
"""Functional Tests for ContentWorkflowsManager

   $Id$
   
"""
import unittest
import re

from zope.interface import Interface
from zope.app.component.interface import nameToInterface
from zope.app import zapi
from zope.app.tests.functional import BrowserTestCase
from zope.app.tests.setup import addUtility
from zope.app.registration.interfaces import ActiveStatus
from zope.app.utility.utility import LocalUtilityService
from zope.app.utility.utility import UtilityRegistration

from zope.app.workflow.stateful.definition import StatefulProcessDefinition
from zope.app.workflow.stateful.interfaces import IStatefulProcessDefinition,\
     IContentWorkflowsManager

class Test(BrowserTestCase):

    def setUp(self):
        BrowserTestCase.setUp(self)
        self.basepath = '/++etc++site/default'
        root = self.getRootFolder()

        sm = zapi.traverse(root, '/++etc++site')
        addUtility(sm,
                   'dummy-definition',
                   IStatefulProcessDefinition,
                   StatefulProcessDefinition()
                   ) 

        response = self.publish(
            self.basepath + '/contents.html',
            basic='mgr:mgrpw')
        
        self.assertEqual(response.getStatus(), 200)
        
        expr = 'zope.app.browser.add.ContentWorkflowsManager.f([0-9]*)'
        m = re.search(expr, response.getBody())
        type_name = m.group(0)
        
        response = self.publish(
            self.basepath + '/contents.html',
            basic='mgr:mgrpw',
            form={'type_name': type_name,
                  'new_value': 'mgr' })

        root = self.getRootFolder()
        default = zapi.traverse(root, '/++etc++site/default')
        rm = default.getRegistrationManager()
        registration = UtilityRegistration(
            'cwm', IContentWorkflowsManager, self.basepath+'/mgr')
        pd_id = rm.addRegistration(registration)
        zapi.traverse(rm, pd_id).status = ActiveStatus
        

    def tearDown(self):
        BrowserTestCase.tearDown(self)


    def test_subscribe(self):
        response = self.publish(
            self.basepath + '/mgr/index.html',
            basic='mgr:mgrpw')
        
        self.assertEqual(response.getStatus(), 200)
        body = ' '.join(response.getBody().split())
        self.assert_(body.find("Subscription state: OFF") >= 0)        

        response = self.publish(
            self.basepath + '/mgr/index.html',
            basic='mgr:mgrpw',
            form={'callSubscribe':'Subscribe'})
        
        self.assertEqual(response.getStatus(), 200)
        body = ' '.join(response.getBody().split())
        self.assert_(body.find("Subscription state: ON") >= 0)        
        root = self.getRootFolder()
        mgr = zapi.traverse(root, self.basepath+'/mgr')
        self.assert_(mgr.isSubscribed())
        
    def test_registry(self):
        response = self.publish(
            self.basepath + '/mgr/registry.html',
            basic='mgr:mgrpw')
        
        self.assertEqual(response.getStatus(), 200)
        body = ' '.join(response.getBody().split())
        self.assert_(body.find(
            '<option value="zope.app.workflow.stateful.interfaces.IState">'
            ) >= 0)        
        self.assert_(body.find(
            '<option value="zope.app.workflow.stateful.interfaces.ITransition">'
            ) >= 0)        

        response = self.publish(
            self.basepath + '/mgr/registry.html',
            basic='mgr:mgrpw',
            form={
            'field.iface':['zope.app.workflow.stateful.interfaces.IState',
                           'zope.app.workflow.stateful.interfaces.ITransition'],
            'field.name':['dummy-definition'],
            'ADD':'Add'
            })
        
        self.assertEqual(response.getStatus(), 200)
        root = self.getRootFolder()
        mgr = zapi.traverse(root, self.basepath+'/mgr')
        ifaces = mgr.getInterfacesForProcessName('dummy-definition')

        self.assert_(nameToInterface(
            None,
            'zope.app.workflow.stateful.interfaces.IState'
            ) in ifaces)
        self.assert_(nameToInterface(
            None,
            'zope.app.workflow.stateful.interfaces.ITransition'
            ) in ifaces)
        self.assertEqual(len(ifaces),2)

        response = self.publish(
            self.basepath + '/mgr/registry.html',
            basic='mgr:mgrpw',
            form={
            'mappings':
            ['dummy-definition:zope.app.workflow.stateful.interfaces.IState',
             'dummy-definition:zope.app.workflow.stateful.interfaces.ITransition'],
            'REMOVE':''
            })

        ifaces = mgr.getInterfacesForProcessName('dummy-definition')
        self.assertEqual(len(ifaces),0)


def test_suite():
    return unittest.makeSuite(Test)

if __name__ == '__main__':
    unittest.main()
