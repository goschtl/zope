# -*- coding: utf-8 -*-
from zope.schema.vocabulary import SimpleVocabulary,SimpleTerm
from zope.schema.interfaces import IVocabularyFactory
from zope.i18n.locales import locales,LOCALEDIR
from zope.i18nmessageid.message import MessageFactory
from zope.i18n.interfaces import ITranslationDomain,INegotiator
from zope.interface import implements
from zope.i18n import interpolate
from zope.component import getUtility
from types import StringType
import glob
import os

# get the locales list
# XXX maybe we should load variants too?
LANGS = []
for name in glob.glob(os.path.join(LOCALEDIR,'??.xml')):
    LANGS.append(os.path.basename(name)[:2])



class DisplayNameTranslationDomain(object):

    """base class for displayname based translation domains"""

    implements(ITranslationDomain)

    def translate(self, msgid, mapping=None, context=None,
                  target_language=None, default=None):
        '''See interface ITranslationDomain'''
        # Find out what the target language should be
        if target_language is None and context is not None:
            # Let's negotiate the language to translate to. :)
            negotiator = getUtility(INegotiator)
            target_language = negotiator.getLanguage(LANGS, context)
        # Find a translation; if nothing is found, use the default
        # value
        if default is None:
            default = msgid
        displayNames = locales.getLocale(target_language).displayNames
        text = getattr(displayNames,
                       self.displayNameAttr).get(msgid,None)
        if text is None:
            text = default
        return interpolate(text, mapping)

class TerritoryTranslationDomain(DisplayNameTranslationDomain):

    """a translation domain which translates territory codes

    >>> d = TerritoryTranslationDomain()
    >>> d.translate('DE',target_language='de')
    u'Deutschland'
    >>> d.translate('DE',target_language='en')
    u'Germany'
    """
    domain='z3c.i18n.iso.territories'
    displayNameAttr = 'territories'

class LanguageTranslationDomain(DisplayNameTranslationDomain):

    """a translation domain which translates language codes

    >>> d = LanguageTranslationDomain()
    >>> d.translate('de',target_language='de')
    u'Deutsch'
    >>> d.translate('de',target_language='en')
    u'German'
    """
    domain='z3c.i18n.iso.languages'
    displayNameAttr = 'languages'

territoryTranslationDomain = TerritoryTranslationDomain()
languageTranslationDomain = LanguageTranslationDomain()

_territories = MessageFactory(TerritoryTranslationDomain.domain)
_languages = MessageFactory(LanguageTranslationDomain.domain)


class LanguageVocabularyFactory(object):

    """a language vocabulary factory

    The factory has a class attribute with messages from the
    iso.languages domain as titles

    >>> fac = LanguageVocabularyFactory()
    >>> voc = fac(None)
    >>> voc
    <zope.schema.vocabulary.SimpleVocabulary object at ...>

    >>> 'de' in voc
    True
    >>> term = voc.getTerm('de')
    >>> term.title.default
    u'German'

    >>> term = voc.getTerm('fr')
    >>> term.title.default
    u'French'

    Let's check if we can translate the title, which is actally a
    Message.

    >>> term.title.domain
    'z3c.i18n.iso.languages'

    >>> from zope import component
    >>> component.provideUtility(languageTranslationDomain,
    ...     name='z3c.i18n.iso.languages')
    >>> from zope.i18n import translate
    >>> translate(term.title,target_language='fr')==u'fran\xe7ais'
    True
    >>> translate(term.title,target_language='de')==u'Franz\xf6sisch'
    True
    """

    implements(IVocabularyFactory)

    def __init__(self):
        self.terms = []
        # excluding fallback etc
        for key,value in [(key,value) for key,value in
            locales.getLocale('en').displayNames.languages.items()
                          if key.lower()==key and len(key)==2]:
            term = SimpleTerm(key,title=_languages(key,value))
            self.terms.append(term)
        self.vocab = SimpleVocabulary(self.terms)


    def __call__(self,context):
        return self.vocab

languageVocabularyFactory = LanguageVocabularyFactory()

class TerritoryVocabularyFactory(object):

    """a territory vocabulary factory

    The factory has a class attribute with messages from the
    iso.territory domain as titles

    >>> fac = TerritoryVocabularyFactory()
    >>> voc = fac(None)
    >>> voc
    <zope.schema.vocabulary.SimpleVocabulary object at ...>

    >>> 'DE' in voc
    True
    >>> term = voc.getTerm('DE')
    >>> term.title.default
    u'Germany'

    >>> u'Fallback' in voc
    False

    >>> from zope import component
    >>> component.provideUtility(territoryTranslationDomain,
    ...     name='z3c.i18n.iso.territories')
    >>> from zope.i18n import translate
    >>> translate(term.title,target_language='fr')
    u'Allemagne'
    >>> translate(term.title,target_language='de')
    u'Deutschland'
    """

    implements(IVocabularyFactory)

    def __init__(self):
        self.terms = []
        # excluding fallback etc
        for key,value in [(key,value) for key,value in
            locales.getLocale('en').displayNames.territories.items()
                          if key.upper()==key and len(key)==2]:
            term = SimpleTerm(key,title=_territories(key,value))
            self.terms.append(term)
        self.vocab = SimpleVocabulary(self.terms)


    def __call__(self,context):
        return self.vocab

territoryVocabularyFactory = TerritoryVocabularyFactory()
