##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""
Functional tests for the unique id utility.

$Id$
"""

import unittest
import re
from zope.app import zapi
from zope.app.tests import ztapi
from zope.app.tests.setup import addUtility
from zope.app.tests.functional import BrowserTestCase

class TestUniqueIdUtility(BrowserTestCase):

    def setUp(self):
        from zope.app.uniqueid import UniqueIdUtility
        from zope.app.uniqueid.interfaces import IUniqueIdUtility

        BrowserTestCase.setUp(self)

        self.basepath = '/++etc++site/default'
        root = self.getRootFolder()

        sm = zapi.traverse(root, '/++etc++site')
        addUtility(sm, 'uniqueid', IUniqueIdUtility, UniqueIdUtility())

        response = self.publish(self.basepath + '/contents.html', basic='mgr:mgrpw')

        self.assertEqual(response.getStatus(), 200)

        expr = 'zope.app.browser.add.UniqueIdUtility.f([0-9]*)'
        m = re.search(expr, response.getBody())
        type_name = m.group(0)

        response = self.publish(
            self.basepath + '/contents.html',
            basic='mgr:mgrpw',
            form={'type_name': type_name,
                  'new_value': 'mgr' })

#        root = self.getRootFolder()
#        default = zapi.traverse(root, '/++etc++site/default')
#        rm = default.getRegistrationManager()
#        registration = UtilityRegistration(
#            'cwm', IUniqueIdUtility, self.basepath+'/uniqueid')
#        pd_id = rm.addRegistration(registration)
#        zapi.traverse(rm, pd_id).status = ActiveStatus

    def test(self):
        response = self.publish(self.basepath + '/uniqueid/@@index.html',
                                basic='mgr:mgrpw')
        self.assertEquals(response.getStatus(), 200)
        self.assert_(response.getBody().find('0 objects') > 0)

        response = self.publish(self.basepath + '/uniqueid/@@populate',
                                basic='mgr:mgrpw')
        self.assertEquals(response.getStatus(), 302)

        response = self.publish(self.basepath + '/uniqueid/@@index.html',
                                basic='mgr:mgrpw')
        self.assertEquals(response.getStatus(), 200)
        body = response.getBody()
        self.assert_(response.getBody().find('2 objects') > 0)
        self.checkForBrokenLinks(response.getBody(), response.getPath(),
                                 basic='mgr:mgrpw')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestUniqueIdUtility))
    return suite


if __name__ == '__main__':
    unittest.main()
