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
"""
$Id: test_translate.py,v 1.3 2002/12/31 02:51:55 jim Exp $
"""

import unittest
from StringIO import StringIO

from zope.app.tests.placelesssetup import PlacelessSetup
from zope.component.adapter import provideAdapter
from zope.component.factory import provideFactory

from zope.app.browser.services.translation.translate \
     import Translate
from zope.app.services.translation.translationservice import \
     TranslationService
from zope.app.services.translation.messagecatalog import \
     MessageCatalog
from zope.i18n.interfaces import IUserPreferredCharsets

from zope.publisher.http import IHTTPRequest
from zope.publisher.http import HTTPCharsets
from zope.publisher.browser import BrowserRequest


class TranslateTest(unittest.TestCase, PlacelessSetup):

    def setUp(self):
        PlacelessSetup.setUp(self)

        # Setup the registries
        provideAdapter(IHTTPRequest, IUserPreferredCharsets, HTTPCharsets)
        provideFactory('Message Catalog', MessageCatalog)

        service = TranslationService('default')

        en_catalog = MessageCatalog('en', 'default')
        de_catalog = MessageCatalog('de', 'default')

        en_catalog.setMessage('short_greeting', 'Hello!')
        de_catalog.setMessage('short_greeting', 'Hallo!')

        en_catalog.setMessage('greeting', 'Hello $name, how are you?')
        de_catalog.setMessage('greeting', 'Hallo $name, wie geht es Dir?')

        service.setObject('en-default-1', en_catalog)
        service.setObject('de-default-1', de_catalog)

        self._view = Translate(service, self._getRequest())


    def _getRequest(self, **kw):
        request = BrowserRequest(StringIO(''), StringIO(), kw)
        request._cookies = {'edit_domains': 'default',
                            'edit_languages': 'en,de'}
        request._traversed_names = ['foo', 'bar']
        return request


    def testGetMessages(self):
        ids = [m[0] for m in self._view.getMessages()]
        ids.sort()
        self.assertEqual(ids, ['greeting', 'short_greeting'])


    def testGetTranslation(self):
        self.assertEqual(self._view.getTranslation('default', 'short_greeting',
                                                   'en'),
                         'Hello!')


    def testGetAllLanguages(self):
        languages = self._view.getAllLanguages()
        languages.sort()
        self.assertEqual(languages, ['de', 'en'])


    def testGetAllDomains(self):
        domains = self._view.getAllDomains()
        domains.sort()
        self.assertEqual(domains, ['default'])


    def testGetEditLanguages(self):
        languages = self._view.getEditLanguages()
        languages.sort()
        self.assertEqual(languages, ['de', 'en'])


    def testGetEditDomains(self):
        domains = self._view.getEditDomains()
        domains.sort()
        self.assertEqual(domains, ['default'])


    # def testEditMessages(self):
    #     pass
    #
    # def testDeleteMessages(self):
    #     pass

    def testAddDeleteLanguage(self):
        self._view.addLanguage('es')
        assert 'es' in self._view.getAllLanguages()
        self._view.deleteLanguages(['es'])
        assert 'es' not in self._view.getAllLanguages()


    def testAddDeleteDomain(self):
        self._view.addDomain('Zope')
        assert 'Zope' in self._view.getAllDomains()
        self._view.deleteDomains(['Zope'])
        assert 'Zope' not in self._view.getAllDomains()


def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase( TranslateTest )

if __name__=='__main__':
    unittest.main()
