from optionstorage.vocabulary import OptionStorageVocabulary
from zope.app.schema.metaconfigure import vocabulary

def optionStorageVocabulary(_context, name):
    def factory(object, name=name):
        return OptionStorageVocabulary(object, name=name)
    vocabulary(_context, name, factory)
