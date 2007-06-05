from zope.app.publisher.browser.metadirectives import IViewDirective
from zope.configuration.fields import MessageID
from zope.interface import Interface
from zope.schema import TextLine


class IOptionStorageDirective(IViewDirective):
    """
    The manageableVocabularies directive is used to create a
    vocabulary editing view for a given interface.
    """

class IOptionStorageOptionsSubdirective(Interface):

    name = TextLine(
                   title=u"Key of option dictionary in storage",
                   required=True,
                   )

    topic = MessageID(
                   title=u"Topic of option dictionary in storage",
                   required=True,
                   )

