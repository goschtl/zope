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
""" ZMI unit tests

$Id: testServiceProvideClass.py,v 1.2 2002/06/10 23:29:19 jim Exp $
"""


import unittest, sys, Interface, os
from Zope.App.ZMI import provideClass

from StringIO import StringIO
from Zope.Configuration.xmlconfig import xmlconfig
from Zope.App.OFS.Services.AddableService.tests.AddableSetup \
     import AddableSetup
from Zope.Configuration.xmlconfig import ZopeXMLConfigurationError
from Zope.ComponentArchitecture import getService

import Zope.App.ZMI
defs_path = os.path.join(
    os.path.split(Zope.App.ZMI.__file__)[0],
    'zmi-meta.zcml')


class MyAddableService:
    pass

class ServiceProvideClassTest(AddableSetup, unittest.TestCase):

    def setUp(self):
        AddableSetup.setUp(self)
        xmlconfig(open(defs_path))

    def testServiceProvideClassDirective(self):
        serviceName = (
            'Zope.App.ZMI.tests.testServiceProvideClass.MyAddableService')
        
        xmlconfig( StringIO('''
        <zopeConfigure
        xmlns="http://namespaces.zope.org/zope"
        xmlns:service="http://namespaces.zope.org/service">

        <service:factoryFromClass
                 id="%s"
                 class="%s"
                 permission="Zope.AddService"
                 title="Stupid Service"
                 description="This is a sample Service" />
      
        </zopeConfigure>
        ''' %(serviceName, serviceName)))

        addables = getService(None,"AddableServices").getAddables(None)
        self.assertEqual(addables[0].id, serviceName)
      
        


def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(ServiceProvideClassTest)

if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
