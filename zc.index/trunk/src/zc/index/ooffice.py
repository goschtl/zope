"""Text extractor for OpenOffice Writer documents (.sxw and .stw).

"""
__docformat__ = "reStructuredText"

import cStringIO
import os
import xml.sax
import xml.sax.handler
import xml.sax.xmlreader
import zipfile

import zope.index.text.interfaces
import zope.interface


class WriterSearchableText(object):
    """Searchable text extractor for OpenOffice Writer documents.

    This can be used for both documents and document templates.

    """

    zope.interface.implements(
        zope.index.text.interfaces.ISearchableText)

    def __init__(self, context):
        self.context = context
        # This could support "classic" files if an adapter is available:
        self._file = zope.file.interfaces.IFile(self.context)

    def getSearchableText(self):
        handler = TextExtractionHandler()
        parser = xml.sax.make_parser()
        parser.setFeature(xml.sax.handler.feature_namespaces, True)
        parser.setContentHandler(handler)
        parser.setEntityResolver(entityResolver)
        f = self._file.open("rb")
        zf = zipfile.ZipFile(f, "r")
        parser.feed(zf.read("content.xml"))
        zf.close()
        f.close()
        return [handler.getText()]


class TextExtractionHandler(xml.sax.handler.ContentHandler):

    def __init__(self):
        self._buffer = []

    def getText(self):
        return u"".join(self._buffer)

    def ensureWhitespace(self, *args):
        if self._buffer and self._buffer[-1] != u" ":
            self._buffer.append(u" ")

    startElement = ensureWhitespace
    endElement = ensureWhitespace

    startElementNS = ensureWhitespace
    endElementNS = ensureWhitespace

    def characters(self, data):
        self._buffer.append(data)


class EntityResolver(object):

    def resolveEntity(self, publicId, systemId):
        source = xml.sax.xmlreader.InputSource()
        source.setByteStream(cStringIO.StringIO(""))
        source.setEncoding("utf-8")
        source.setPublicId(publicId)
        source.setSystemId(systemId)
        return source

entityResolver = EntityResolver()
