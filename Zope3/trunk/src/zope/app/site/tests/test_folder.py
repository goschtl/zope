##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Site-management folder tests

$Id: test_folder.py,v 1.1 2004/03/13 15:21:57 srichter Exp $
"""
import unittest
from zope.app.services.tests.test_registrationmanager \
     import RegistrationManagerContainerTests


class TestSomething(RegistrationManagerContainerTests, unittest.TestCase):
    "Test registration manager access"
        

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSomething))
    return suite


if __name__ == '__main__':
    unittest.main()
