##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
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

"""
$Id$
"""
__docformat__ = 'restructuredtext'

from zope.interface import classProvides
from zope.interface.declarations import implements

from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

from zope.app.zapi import getUtility
from zope.app.i18n.interfaces import ILocalTranslationDomain

from z3c.language.negotiator import interfaces


class OfferedLanguagesVocabulary(SimpleVocabulary):
    """A vocabulary of available (offered) languages."""

    implements(interfaces.IOfferedLanguagesVocabulary)

    def __init__(self, context):
        terms = []
        
        # collect offered languages
        negotiator = getUtility(interfaces.INegotiator)
        languages = negotiator.offeredLanguages

        for lang in languages:
            terms.append(SimpleTerm(lang, lang, lang))

        terms.sort(lambda lhs, rhs: cmp(lhs.title, rhs.title))
        super(OfferedLanguagesVocabulary, self).__init__(terms)


class AvailableTranslationDomainLanguagesVocabulary(SimpleVocabulary):
    """A vocabular of available languages from a translation domain."""

    implements(interfaces.IAvailableTranslationDomainLanguagesVocabulary)

    def __init__(self, context, domain='zope'):
        terms = []
        
        # collect languages from translation domain
        trans_domain = getUtility(ILocalTranslationDomain, domain)
        languages = trans_domain.getAvailableLanguages()

        for lang in languages:
            terms.append(SimpleTerm(lang, lang, lang))

        terms.sort(lambda lhs, rhs: cmp(lhs.title, rhs.title))
        super(AvailableTranslationDomainLanguagesVocabulary, self).__init__(
            terms)


class AvailableTranslationDomainLanguagesVocabularyForZ3C(
    AvailableTranslationDomainLanguagesVocabulary):
    """AvailableTranslationDomainLanguagesVocabulary for z3c domain."""

    classProvides(IVocabularyFactory)

    def __init__(self, context, ):
        super(AvailableTranslationDomainLanguagesVocabulary,self).__init__(
            context, domain='z3c')
