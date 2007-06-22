from zope.schema.interfaces import IVocabularyTokenized
from zope.schema.vocabulary import SimpleTerm
from zope.interface import implements
from zope.app import zapi

from zope.security.management import getInteraction
from zope.i18n.negotiator import negotiator

from optionstorage.interfaces import IOptionStorage, IOptionStorageVocabulary
from optionstorage import OptionStorageKey, queryOptionStorage


class OptionStorageVocabulary(object):

    # Order matters here. We want our multi-view adapter to be chosen
    # before the IVocabulary default one.
    implements(IOptionStorageVocabulary, IVocabularyTokenized)

    def __init__(self, context, name):
        self.dict = queryOptionStorage(context, name)
        if self.dict:
            # Workaround. Hopefully, in the future titles will be
            # computed as a view.
            interaction = getInteraction()
            request = interaction.participations[0]
            self.language = negotiator.getLanguage(self.dict.getLanguages(),
                                                   request)
            self.defaultlanguage = self.dict.getDefaultLanguage()

    def __contains__(self, key):
        if self.dict:
            try:
                self.dict.getValue(key, self.language)
                return True
            except KeyError:
                try:
                    self.dict.getValue(key, self.defaultlanguage)
                    return True
                except KeyError:
                    pass
        return False

    def getTerm(self, key):
        if self.dict:
            try:
                value = self.dict.getValue(key, self.language)
                return SimpleTerm(key, title=value)
            except KeyError:
                try:
                    value = self.dict.getValue(key, self.defaultlanguage)
                    return SimpleTerm(key, title=value)
                except KeyError:
                    pass
        raise LookupError

    def getTermByToken(self, token):
        return self.getTerm(token)

    def __iter__(self):
        if self.dict:
            for key in self.dict.getKeys():
                try:
                    yield self.getTerm(key)
                except LookupError:
                    pass

    def __len__(self):
        count = 0
        if self.dict:
            marker = object()
            for key in self.dict.getKeys():
                if (self.dict.queryValue(key, self.language,
                                        marker) is not marker
                    or self.dict.queryValue(key, self.defaultlanguage,
                                            marker) is not marker):
                
                    count += 1
        return count

    def getDefaultKey(self):
        if self.dict:
            return self.dict.getDefaultKey()

