##############################################################################
#
# Copyright (c) 2005 Five Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Mimick Zope3 i18n machinery for Zope 2

$Id$
"""
from zope.i18n import interpolate
from zope.i18n.interfaces import ITranslationDomain
from zope.i18nmessageid import MessageID
from zope.app import zapi

from Products.PageTemplates import GlobalTranslationService as GTS

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
            ts.translate(domain, msgid, mapping, context, target_language,
                         default)

        # in Zope3, context is adapted to IUserPreferredLanguages,
        # which means context should be the request in this case.
        if context is not None:
            context = context.REQUEST
        return util.translate(msgid, mapping, context, target_language, default)
