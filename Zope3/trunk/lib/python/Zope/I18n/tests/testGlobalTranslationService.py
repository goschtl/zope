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
"""This module tests the regular persistent Translation Service.

$Id: testGlobalTranslationService.py,v 1.3 2002/06/16 18:25:14 srichter Exp $
"""
import unittest, sys, os
from Zope.I18n.GlobalTranslationService import GlobalTranslationService
from Zope.I18n.GettextMessageCatalog import GettextMessageCatalog 
from testIReadTranslationService import TestIReadTranslationService

def testdir():
    from Zope.I18n import tests
    return os.path.dirname(tests.__file__)


class TestGlobalTranslationService(TestIReadTranslationService):

    def _getTranslationService(self):
        service = GlobalTranslationService('default') 
        path = testdir()
        en_catalog = GettextMessageCatalog('en', 'default',
                                           os.path.join(path, 'en-default.mo'))
        de_catalog = GettextMessageCatalog('de', 'default',
                                           os.path.join(path, 'de-default.mo'))
        service.addCatalog(en_catalog)
        service.addCatalog(de_catalog)
        return service


def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(TestGlobalTranslationService)


if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
