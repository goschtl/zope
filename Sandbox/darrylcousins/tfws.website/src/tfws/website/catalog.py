import zope.interface
from zope.index.text import textindex
from zope.dublincore.interfaces import IZopeDublinCore
from zope.app.catalog.text import ITextIndex
from zope.app.container import contained

from zc.catalog import catalogindex

from tfws.website import interfaces

class TextIndex(textindex.TextIndex, contained.Contained):

    # not really true but needed by query.Text
    zope.interface.implements(ITextIndex)

    def index_doc(self, docid, obj):
        text = ''
        if interfaces.IContent.providedBy(obj):
            text += obj.title + ' '
            text += obj.description + ' '
            text += obj.keyword + ' '
            text += obj.body
        return super(TextIndex, self).index_doc(docid, text)

    def __repr__(self):
        return '<%s for IFeed>' %self.__class__.__name__


def setup_catalog(catalog):
    """Configure catalog for the site."""

    # Feed text index
    catalog['text'] = TextIndex()

    # Dublin Core Indices
    catalog['creator'] = catalogindex.SetIndex('creators', IZopeDublinCore)
    catalog['created'] = catalogindex.DateTimeValueIndex(
        'created', IZopeDublinCore)
