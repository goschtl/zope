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

$Id: test_translationservice.py,v 1.5 2003/02/12 02:17:35 seanb Exp $
"""
import unittest, sys

from zope.app.services.servicenames import Factories

from zope.app.component.metaconfigure import handler

from zope.app.services.translation.translationservice import \
     TranslationService
from zope.app.services.translation.messagecatalog import \
     MessageCatalog
from zope.i18n.tests.test_ireadtranslationservice import \
     TestIReadTranslationService
from zope.i18n.tests.test_iwritetranslationservice import \
     TestIWriteTranslationService
from zope.i18n.tests.test_isynctranslationservice import \
     TestISyncTranslationService


class TestTranslationService(TestIReadTranslationService,
                             TestIWriteTranslationService,
                             TestISyncTranslationService):


    def setUp(self):
        TestISyncTranslationService.setUp(self)
        TestIReadTranslationService.setUp(self)
        TestIWriteTranslationService.setUp(self)
        handler(Factories, 'provideFactory', 'Message Catalog',
                MessageCatalog)


    def _getTranslationService(self):
        service = TranslationService('default')

        en_catalog = MessageCatalog('en', 'default')
        de_catalog = MessageCatalog('de', 'default')
        # Populate the catalogs with translations of a message id
        en_catalog.setMessage('short_greeting', 'Hello!', 10)
        de_catalog.setMessage('short_greeting', 'Hallo!', 10)
        # And another message id with interpolation placeholders
        en_catalog.setMessage('greeting', 'Hello $name, how are you?', 0)
        de_catalog.setMessage('greeting', 'Hallo $name, wie geht es Dir?', 0)

        service.setObject('en-default-1', en_catalog)
        service.setObject('de-default-1', de_catalog)

        return service

    def testParameterNames(self):
        service = self._service
        translate = service.translate
        eq = self.assertEqual
        raises = self.assertRaises
        # Test that the second argument is called `msgid'
        eq(translate('default', msgid='short_greeting', target_language='en'),
           'Hello!')
        # This is what the argument used to be called
        raises(TypeError, translate, 'default', source='short_greeting',
               target_language='en')


def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(TestTranslationService)


if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
