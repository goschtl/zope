
from zope import interface, component
import zope.index.text.interfaces
import zope.file.interfaces
import zope.mimetype.interfaces

class TextSearchableText(object):
    """Searchable text extractor for simple text documents.
    """

    interface.implements(
        zope.index.text.interfaces.ISearchableText)

    def __init__(self, context):
        self.context = context
        # This could support "classic" files if an adapter is available:
        self._file = zope.file.interfaces.IFile(self.context)

    def get_unicode(self):
        ci = zope.mimetype.interfaces.IContentInfo(self._file)
        if "charset" in ci.effectiveParameters:
            f = self._file.open('rb')
            data = f.read()
            f.close()
            return ci.decode(data)
        # return None

    def getSearchableText(self):
        out = self.get_unicode()
        if out is not None:
            return [out]
        return ()
