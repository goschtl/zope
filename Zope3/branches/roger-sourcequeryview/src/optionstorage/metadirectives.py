from zope.interface import Interface
from zope.schema import TextLine

class IOptionStorageVocabularyDirective(Interface):
    """
    Define a named vocabulary fetching information from an option storage.
    """

    name = TextLine(
                title=u"Name",
                description=u"Provides the name for the option storage "\
                            u"vocabulary.",
                required=True)
