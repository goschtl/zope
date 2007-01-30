from zope.app.component.vocabulary import UtilityVocabulary
from ZODB.interfaces import IDatabase

class DatabaseVocabulary(UtilityVocabulary):
    interface = IDatabase
    nameOnly = True
