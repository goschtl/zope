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
"""Test the workflow ZCML namespace directives.

$Id: test_directives.py,v 1.1 2003/08/22 21:27:36 srichter Exp $
"""
import unittest

from zope.app import zapi
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.configuration import xmlconfig

from book.smileyutility import tests 
from book.smileyutility.interfaces import ISmileyTheme

class DirectivesTest(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(DirectivesTest, self).setUp()
        self.context = xmlconfig.file("smiley.zcml", tests)

    def test_SmileyDirectives(self):
        self.assertEqual(
            zapi.getUtility(ISmileyTheme,
                            'default')._GlobalSmileyTheme__smileys,
            {u':(': u'/++resource++plain__sad.png'})
        self.assertEqual(
            zapi.getUtility(ISmileyTheme,
                            'plain')._GlobalSmileyTheme__smileys,
            {u':(': u'/++resource++plain__sad.png'})
        self.assertEqual(
            zapi.getUtility(ISmileyTheme,
                            'yazoo')._GlobalSmileyTheme__smileys,
            {u':)': u'/++resource++yazoo__smile.png',
             u':(': u'/++resource++yazoo__sad.png'})

    def test_defaultTheme(self):
        self.assertEqual(zapi.getUtility(ISmileyTheme, 'default'),
                         zapi.getUtility(ISmileyTheme, 'plain'))

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(DirectivesTest),
        ))

if __name__ == '__main__':
    unittest.main()
