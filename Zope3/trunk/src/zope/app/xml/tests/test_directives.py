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
"""Test the 'xml' ZCML namespace directives.

$Id: test_directives.py,v 1.1 2003/08/01 20:18:08 srichter Exp $
"""
import unittest
import zope.app.xml
from zope.configuration import xmlconfig
from zope.app.component.globalinterfaceservice import interfaceService

class DirectivesTest(unittest.TestCase):

    def test_schemaInterface(self):
        self.assertEqual(interfaceService.searchInterfaceIds(), [])
        self.context = xmlconfig.file("tests/xml.zcml", zope.app.xml)
        self.assertEqual(interfaceService.searchInterfaceIds(),
                          [u'http://www.zope3.org/Zope3'])


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(DirectivesTest),
        ))

if __name__ == '__main__':
    unittest.main()
