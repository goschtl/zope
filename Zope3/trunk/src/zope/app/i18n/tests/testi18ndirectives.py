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
"""Test the gts ZCML namespace directives.

$Id: testi18ndirectives.py,v 1.4 2003/07/28 22:20:25 jim Exp $
"""
import os
import unittest

from cStringIO import StringIO

from zope.component.tests.placelesssetup import PlacelessSetup
from zope.configuration import xmlconfig

import zope.app.i18n
import zope.i18n.tests

from zope.i18n.globaltranslationservice import translationService


template = """<zopeConfigure
   xmlns='http://namespaces.zope.org/zope'
   xmlns:gts='http://namespaces.zope.org/gts'>
   xmlns:test='http://www.zope.org/NS/Zope3/test'>
   %s
   </zopeConfigure>"""


class DirectivesTest(PlacelessSetup, unittest.TestCase):

    # XXX: tests for other directives needed

    def setUp(self):
        PlacelessSetup.setUp(self)
        self.context = xmlconfig.file('meta.zcml', zope.app.i18n)

    def testRegisterTranslations(self):
        eq = self.assertEqual
        eq(translationService._catalogs, {})
        xmlconfig.string(
            template % '''
            <configure package="zope.i18n.tests">
            <gts:registerTranslations directory="./locale" />
            </configure>
            ''', self.context)
        path = os.path.join(os.path.dirname(zope.i18n.tests.__file__),
                            'locale', 'en',
                            'LC_MESSAGES', 'zope-i18n.mo')
        eq(translationService._catalogs,
           {('en', 'zope-i18n'): [unicode(path)]})

    def testDefaultLanguages(self):
        eq = self.assertEqual
        eq(translationService._fallbacks, ['en'])
        xmlconfig.string(
            template % '''
            <gts:defaultLanguages languages="de nl xx" />
            ''', self.context)
        eq(translationService._fallbacks, ['de', 'nl', 'xx'])


def test_suite():
    return unittest.makeSuite(DirectivesTest)

if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
