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

$Id: test_translationservice.py,v 1.9 2003/04/17 20:05:12 bwarsaw Exp $
"""
import sys
import unittest

from zope.interface.verify import verifyObject
from zope.app.services.servicenames import Factories
from zope.app.component.metaconfigure import handler

from zope.i18n.interfaces import IUserPreferredLanguages, ITranslationService
from zope.app.services.translation.translationservice import \
     TranslationService
from zope.app.interfaces.services.translation import ISyncTranslationService
from zope.app.services.translation.messagecatalog import \
     MessageCatalog
from zope.i18n.tests.test_itranslationservice import \
     TestITranslationService
from zope.app.component.metaconfigure import provideService, managerHandler


class Environment:

    __implements__ = IUserPreferredLanguages

    def __init__(self, langs=()):
        self.langs = langs

    def getPreferredLanguages(self):
        return self.langs


class TestILocalTranslationService:

    def _getTranslationService(self):
        """This should be overwritten by every clas that inherits this test.

           We expect the TranslationService to contain exactly 2 languages:
           de and en
        """

    def setUp(self):
        self._service = self._getTranslationService()
        assert verifyObject(ITranslationService, self._service)
        managerHandler('defineService', 'Translation', ITranslationService)
        provideService('Translation', self._service, 'zope.Public')


    def _getDomains(self, service):
        domains = service.getAllDomains()
        domains.sort()
        return domains


    def testGetAddDeleteDomain(self):
        service = self._service
        service.addLanguage('de')
        d = self._getDomains(service)
        self.assertEqual(service.getAllDomains(), d+[])
        service.addDomain('test')
        self.assertEqual(service.getAllDomains(), d+['test'])
        service.addDomain('test2')
        self.assertEqual(service.getAllDomains(), d+['test', 'test2'])
        self.assertEqual(service.getAvailableDomains('de'),
                         d+['test', 'test2'])
        service.deleteDomain('test')
        self.assertEqual(service.getAllDomains(), d+['test2'])
        service.deleteDomain('test2')
        self.assertEqual(service.getAllDomains(), d+[])


    def _getLanguages(self, service):
        languages = service.getAllLanguages()
        languages.sort()
        return languages


    def testGetAddDeleteLanguage(self):
        service = self._service
        service.addDomain('test')
        langs = self._getLanguages(service)
        service.addLanguage('es')
        self.assertEqual(self._getLanguages(service), langs+['es'])
        service.addLanguage('fr')
        self.assertEqual(self._getLanguages(service), langs+['es', 'fr'])
        self.assertEqual(service.getAvailableLanguages('test'),
                         langs+['es', 'fr'])
        service.deleteLanguage('es')
        self.assertEqual(self._getLanguages(service), langs+['fr'])
        service.deleteLanguage('fr')
        self.assertEqual(self._getLanguages(service), langs)


    def testAddUpdateDeleteMessage(self):
        service = self._service
        self.assertEqual(service.translate('greeting', 'test',
                                           target_language='de'),
                         None)
        self.assertEqual(service.translate('greeting', 'test',
                                           target_language='de', default=42),
                         42)
        service.addMessage('test', 'greeting', 'Hallo!', 'de')
        self.assertEqual(service.translate('greeting', 'test',
                                           target_language='de'), 'Hallo!')
        service.updateMessage('test', 'greeting', 'Hallo Ihr da!', 'de')
        self.assertEqual(service.translate('greeting', 'test',
                                           target_language='de'),
                         'Hallo Ihr da!')
        service.deleteMessage('test', 'greeting', 'de')
        self.assertEqual(service.translate('greeting', 'test',
                                           target_language='de'), None)


    def _getMessageIds(self, service, domain, filter="%"):
        ids = service.getMessageIdsOfDomain(domain, filter)
        ids.sort()
        return ids


    def testFilteredGetAllMessageIdsOfDomain(self):
        service = self._service
        service.addMessage('test',  'greeting', 'Greeting!', 'en')
        service.addMessage('test',  'greeting2', 'Greeting 2!', 'en')
        service.addMessage('test2', 'greeting3', 'Greeting 3!', 'en')
        service.addMessage('test2', 'greeting4', 'Greeting 4!', 'en')

        self.assertEqual(self._getMessageIds(service, 'test'),
                         ['greeting', 'greeting2'])
        self.assertEqual(self._getMessageIds(service, 'test2'),
                         ['greeting3', 'greeting4'])
        self.assertEqual(self._getMessageIds(service, 'test', 'greeting'),
                         ['greeting', 'greeting2'])
        self.assertEqual(self._getMessageIds(service, 'test', '%2'),
                         ['greeting2'])
        self.assertEqual(self._getMessageIds(service, 'test', 'gre%2'),
                         ['greeting2'])
        self.assertEqual(self._getMessageIds(service, 'test2', 'gre%'),
                         ['greeting3', 'greeting4'])



# A test mixing -- don't add this to the suite
class TestISyncTranslationService:

    foreign_messages = [
        # Message that is not locally available
        {'domain': 'default', 'language': 'en', 'msgid': 'test',
         'msgstr': 'Test', 'mod_time': 0},
        # This message is newer than the local one.
        {'domain': 'default', 'language': 'de', 'msgid': 'short_greeting',
         'msgstr': 'Hallo.', 'mod_time': 20},
        # This message is older than the local one.
        {'domain': 'default', 'language': 'en', 'msgid': 'short_greeting',
         'msgstr': 'Hello', 'mod_time': 0},
        # This message is up-to-date.
        {'domain': 'default', 'language': 'en', 'msgid': 'greeting',
         'msgstr': 'Hello $name, how are you?', 'mod_time': 0}]


    local_messages = [
        # This message is older than the foreign one.
        {'domain': 'default', 'language': 'de', 'msgid': 'short_greeting',
         'msgstr': 'Hallo!', 'mod_time': 10},
        # This message is newer than the foreign one.
        {'domain': 'default', 'language': 'en', 'msgid': 'short_greeting',
         'msgstr': 'Hello!', 'mod_time': 10},
        # This message is up-to-date.
        {'domain': 'default', 'language': 'en', 'msgid': 'greeting',
         'msgstr': 'Hello $name, how are you?', 'mod_time': 0},
        # This message is only available locally.
        {'domain': 'default', 'language': 'de', 'msgid': 'greeting',
         'msgstr': 'Hallo $name, wie geht es Dir?', 'mod_time': 0},
        ]


    # This should be overwritten by every clas that inherits this test
    def _getTranslationService(self):
        pass


    def setUp(self):
        self._service = self._getTranslationService()
        assert verifyObject(ISyncTranslationService, self._service)


    def testGetMessagesMapping(self):
        mapping = self._service.getMessagesMapping(['default'], ['de', 'en'],
                                                  self.foreign_messages)
        self.assertEqual(mapping[('test', 'default', 'en')],
                         (self.foreign_messages[0], None))
        self.assertEqual(mapping[('short_greeting', 'default', 'de')],
                         (self.foreign_messages[1], self.local_messages[0]))
        self.assertEqual(mapping[('short_greeting', 'default', 'en')],
                         (self.foreign_messages[2], self.local_messages[1]))
        self.assertEqual(mapping[('greeting', 'default', 'en')],
                         (self.foreign_messages[3], self.local_messages[2]))
        self.assertEqual(mapping[('greeting', 'default', 'de')],
                         (None, self.local_messages[3]))


    def testSynchronize(self):
        service = self._service
        mapping = service.getMessagesMapping(['default'], ['de', 'en'],
                                             self.foreign_messages)
        service.synchronize(mapping)

        self.assertEqual(service.getMessage('test', 'default', 'en'),
                         self.foreign_messages[0])
        self.assertEqual(service.getMessage('short_greeting', 'default', 'de'),
                         self.foreign_messages[1])
        self.assertEqual(service.getMessage('short_greeting', 'default', 'en'),
                         self.local_messages[1])
        self.assertEqual(service.getMessage('greeting', 'default', 'en'),
                         self.local_messages[2])
        self.assertEqual(service.getMessage('greeting', 'default', 'en'),
                         self.foreign_messages[3])
        self.assertEqual(service.getMessage('greeting', 'default', 'de'),
                         None)


class TestTranslationService(unittest.TestCase,
                             TestITranslationService,
                             TestILocalTranslationService,
                             TestISyncTranslationService):


    def setUp(self):
        TestISyncTranslationService.setUp(self)
        TestITranslationService.setUp(self)
        TestILocalTranslationService.setUp(self)
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
        eq(translate('short_greeting', 'default', target_language='en'),
           'Hello!')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestTranslationService))
    return suite
