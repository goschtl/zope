##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Mimick Zope3 i18n machinery for Zope 2

$Id$
"""
from zope.i18n import interpolate
from zope.i18n.interfaces import ITranslationDomain, IUserPreferredLanguages
from zope.i18nmessageid import MessageID
from zope.app import zapi
from zope.publisher.browser import BrowserLanguages

from Products.PageTemplates import GlobalTranslationService as GTS

class FiveTranslationService:
    """Translation service that delegates to ``zope.i18n`` machinery.
    """
    # this is mostly a copy of zope.i18n.translate, with modifications
    # regarding fallback and Zope 2 compatability
    def translate(self, domain, msgid, mapping=None,
                  context=None, target_language=None, default=None):
        if isinstance(msgid, MessageID):
            domain = msgid.domain
            default = msgid.default
            mapping = msgid.mapping

        util = zapi.queryUtility(ITranslationDomain, domain)

        if util is None:
            # fallback to translation service that was registered,
            # DummyTranslationService the worst
            ts = _fallback_translation_service
            return ts.translate(domain, msgid, mapping=mapping, context=context,
                                target_language=target_language, default=default)

        # in Zope3, context is adapted to IUserPreferredLanguages,
        # which means context should be the request in this case.
        return util.translate(msgid, mapping=mapping, context=context,
                              target_language=target_language, default=default)

def languagesFromRequest(context):
    """This adapter factory dispatches adapter lookup to the request
    instead of the current context object.

    In Zope 2, the preferred languages can be chosen placefully which
    is why the FiveTranslationService passes the general context
    object as a translation context.  In Zope 3, the request object is
    normally used for this; we mimic this behaviour here by being an
    adapter factory for * and dispatching to an adapter lookup on the
    request."""
    return IUserPreferredLanguages(context.REQUEST)

class FiveBrowserLanguages(BrowserLanguages):

    def getPreferredLanguages(self):
        language_list = super(FiveBrowserLanguages, self).getPreferredLanguages()

        # Support for getting a user selected languages
        # 1. From Localizer
        selected_language = self.request.cookies.get('LOCALIZER_LANGUAGE', None)

        if selected_language is None:
            # 2. From PlacelessTranslationService.
            selected_language = self.request.cookies.get('pts_language', None)

        if selected_language:
            # Make sure the selected language is first in the list
            if not language_list:
                return [selected_language]
            if selected_language == language_list[0]:
                # Already first
                return language_list
            if selected_language in language_list:
                language_list.remove(selected_language)
            language_list.insert(0, selected_language)

        return language_list

# these are needed for the monkey
_fallback_translation_service = GTS.DummyTranslationService()
fiveTranslationService = FiveTranslationService()

def getGlobalTranslationService():
    return fiveTranslationService

def setGlobalTranslationService(newservice):
    global _fallback_translation_service
    oldservice, _fallback_translation_service = \
        _fallback_translation_service, newservice
    return oldservice

def monkey():
    # get the services that has been registered so far and plug in our
    # new one
    global _fallback_translation_service
    _fallback_translation_service = \
        GTS.setGlobalTranslationService(fiveTranslationService)

    # now override the getter/setter so that noone else can mangle
    # with it anymore
    GTS.getGlobalTranslationService = getGlobalTranslationService
    GTS.setGlobalTranslationService = setGlobalTranslationService
