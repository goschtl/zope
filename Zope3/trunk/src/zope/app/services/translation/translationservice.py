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
"""This is the standard, placeful Translation Service for TTW development.

$Id: translationservice.py,v 1.10 2003/05/01 19:35:35 faassen Exp $
"""
import re

from zodb.btrees.OOBTree import OOBTree

from zope.component import createObject, getService
from zope.app.component.nextservice import queryNextService

from zope.app.container.btree import BTreeContainer

from zope.app.interfaces.services.service import ISimpleService

from zope.i18n.negotiator import negotiator
from zope.app.interfaces.services.translation import ILocalTranslationService
from zope.i18n.simpletranslationservice import SimpleTranslationService


class TranslationService(BTreeContainer, SimpleTranslationService):

    __implements__ =  ILocalTranslationService, ISimpleService

    def __init__(self, default_domain='global'):
        super(TranslationService, self).__init__()
        self._catalogs = OOBTree()
        self.default_domain = default_domain


    def _registerMessageCatalog(self, language, domain, catalog_name):
        if (language, domain) not in self._catalogs.keys():
            self._catalogs[(language, domain)] = []

        mc = self._catalogs[(language, domain)]
        mc.append(catalog_name)


    def _unregisterMessageCatalog(self, language, domain, catalog_name):
        self._catalogs[(language, domain)].remove(catalog_name)


    def setObject(self, name, object):
        'See IWriteContainer'
        super(TranslationService, self).setObject(name, object)
        self._registerMessageCatalog(object.getLanguage(), object.getDomain(),
                                     name)
        return name

    def __delitem__(self, name):
        'See IWriteContainer'
        object = self[name]
        super(TranslationService, self).__delitem__(name)
        self._unregisterMessageCatalog(object.getLanguage(),
                                       object.getDomain(), name)

    def translate(self, msgid, domain=None, mapping=None, context=None,
                  target_language=None, default=None):
        """See interface ITranslationService"""
        if domain is None:
            domain = self.default_domain

        if target_language is None and context is not None:
            avail_langs = self.getAvailableLanguages(domain)
            # Let's negotiate the language to translate to. :)
            negotiator = getService(self, 'LanguageNegotiation')
            target_language = negotiator.getLanguage(avail_langs, context)

        # Get the translation. Default is the source text itself.
        catalog_names = self._catalogs.get((target_language, domain), [])

        for name in catalog_names:
            catalog = super(TranslationService, self).__getitem__(name)
            text = catalog.queryMessage(msgid)
            if text is not None:
                break
        else:
            # If nothing found, delegate to
            # a translation server higher up the tree.
            ts = queryNextService(self, 'Translation')
            if ts is not None:
                return ts.translate(msgid, domain, mapping, context,
                                    target_language, default=default)
            else:
                return default

        # Now we need to do the interpolation
        return self.interpolate(text, mapping)

    def getMessageIdsOfDomain(self, domain, filter='%'):
        'See IWriteTranslationService'
        filter = filter.replace('%', '.*')
        filter_re = re.compile(filter)

        msgids = {}
        languages = self.getAvailableLanguages(domain)
        for language in languages:
            for name in self._catalogs[(language, domain)]:
                for msgid in self[name].getMessageIds():
                    if filter_re.match(msgid) >= 0:
                        msgids[msgid] = None
        return msgids.keys()


    def getMessagesOfDomain(self, domain):
        'See IWriteTranslationService'
        messages = []
        languages = self.getAvailableLanguages(domain)
        for language in languages:
            for name in self._catalogs[(language, domain)]:
                messages += self[name].getMessages()
        return messages


    def getMessage(self, msgid, domain, language):
        'See IWriteTranslationService'
        for name in self._catalogs.get((language, domain), []):
            try:
                return self[name].getFullMessage(msgid)
            except:
                pass
        return None

    def getAllLanguages(self):
        'See IWriteTranslationService'
        languages = {}
        for key in self._catalogs.keys():
            languages[key[0]] = None
        return languages.keys()


    def getAllDomains(self):
        'See IWriteTranslationService'
        domains = {}
        for key in self._catalogs.keys():
            domains[key[1]] = None
        return domains.keys()


    def getAvailableLanguages(self, domain):
        'See IWriteTranslationService'
        identifiers = self._catalogs.keys()
        identifiers = filter(lambda x, d=domain: x[1] == d, identifiers)
        languages = map(lambda x: x[0], identifiers)
        return languages


    def getAvailableDomains(self, language):
        'See IWriteTranslationService'
        identifiers = self._catalogs.keys()
        identifiers = filter(lambda x, l=language: x[0] == l, identifiers)
        domains = map(lambda x: x[1], identifiers)
        return domains


    def addMessage(self, domain, msgid, msg, language, mod_time=None):
        'See IWriteTranslationService'
        if not self._catalogs.has_key((language, domain)):
            if language not in self.getAllLanguages():
                self.addLanguage(language)
            if domain not in self.getAllDomains():
                self.addDomain(domain)

        catalog_name = self._catalogs[(language, domain)][0]
        catalog = self[catalog_name]
        catalog.setMessage(msgid, msg, mod_time)


    def updateMessage(self, domain, msgid, msg, language, mod_time=None):
        'See IWriteTranslationService'
        catalog_name = self._catalogs[(language, domain)][0]
        catalog = self[catalog_name]
        catalog.setMessage(msgid, msg, mod_time)


    def deleteMessage(self, domain, msgid, language):
        'See IWriteTranslationService'
        catalog_name = self._catalogs[(language, domain)][0]
        catalog = self[catalog_name]
        catalog.deleteMessage(msgid)


    def addLanguage(self, language):
        'See IWriteTranslationService'
        domains = self.getAllDomains()
        if not domains:
            domains = [self.default_domain]

        for domain in domains:
            catalog = createObject(self, 'Message Catalog', language, domain)
            self.setObject('%s-%s' %(domain, language), catalog)


    def addDomain(self, domain):
        'See IWriteTranslationService'
        languages = self.getAllLanguages()
        if not languages:
            languages = ['en']

        for language in languages:
            catalog = createObject(self, 'Message Catalog', language, domain)
            self.setObject('%s-%s' %(domain, language), catalog)


    def deleteLanguage(self, language):
        'See IWriteTranslationService'
        domains = self.getAvailableDomains(language)
        for domain in domains:
            # Delete all catalogs from the data storage
            for name in self._catalogs[(language, domain)]:
                if self.has_key(name):
                    del self[name]
            # Now delete the specifc catalog registry for this lang/domain
            del self._catalogs[(language, domain)]

    def deleteDomain(self, domain):
        'See IWriteTranslationService'
        languages = self.getAvailableLanguages(domain)
        for language in languages:
            # Delete all catalogs from the data storage
            for name in self._catalogs[(language, domain)]:
                if self.has_key(name):
                    del self[name]
            # Now delete the specifc catalog registry for this lang/domain
            del self._catalogs[(language, domain)]

    def getMessagesMapping(self, domains, languages, foreign_messages):
        'See ISyncTranslationService'
        mapping = {}
        # Get all relevant local messages
        local_messages = []
        for domain in domains:
            for language in languages:
                for name in self._catalogs.get((language, domain), []):
                    local_messages += self[name].getMessages()


        for fmsg in foreign_messages:
            ident = (fmsg['msgid'], fmsg['domain'], fmsg['language'])
            mapping[ident] = (fmsg, self.getMessage(*ident))

        for lmsg in local_messages:
            ident = (lmsg['msgid'], lmsg['domain'], lmsg['language'])
            if ident not in mapping.keys():
                mapping[ident] = (None, lmsg)

        return mapping


    def synchronize(self, messages_mapping):
        'See ISyncTranslationService'

        for value in messages_mapping.values():
            fmsg = value[0]
            lmsg = value[1]
            if fmsg is None:
                self.deleteMessage(lmsg['domain'], lmsg['msgid'],
                                   lmsg['language'])
            elif lmsg is None:
                self.addMessage(fmsg['domain'], fmsg['msgid'],
                                fmsg['msgstr'], fmsg['language'],
                                fmsg['mod_time'])
            elif fmsg['mod_time'] > lmsg['mod_time']:
                self.updateMessage(fmsg['domain'], fmsg['msgid'],
                                   fmsg['msgstr'], fmsg['language'],
                                   fmsg['mod_time'])

    #
    ############################################################
