"""Searchable text extraction for RTF documents.

"""
__docformat__ = "reStructuredText"

import zope.file.interfaces
import zope.index.text.interfaces
import zope.interface

import zc.index.rtflib


class RtfSearchableText(object):

    zope.interface.implements(
        zope.index.text.interfaces.ISearchableText)

    def __init__(self, context):
        self.context = context
        self._file = zope.file.interfaces.IFile(context)

    def getSearchableText(self):
        handler = TextExtractionHandler()
        parser = zc.index.rtflib.RtfReader(handler)
        f = self._file.open("rb")
        try:
            parser.parseStream(f)
        finally:
            f.close()
        return [handler.getText()]


class TextExtractionHandler(object):

    def __init__(self):
        self._buffers = [[]]

    def getText(self):
        return u"".join(self._buffers[0])

    def command(self, cmd, arg):
        if cmd in ("line", "par", "pard", "tab"):
            self._buffers[-1].append(u"\n")
        elif cmd in ("colortbl", "filetbl", "fonttbl", "info", "pgdsc", "stylesheet"):
            # divert output to someplace that will be discarded
            self._buffers[-1] = []

    def characters(self, text):
        self._buffers[-1].append(text)

    def startGroup(self):
        self._buffers.append(self._buffers[-1])

    def endGroup(self):
        del self._buffers[-1]

    def startDocument(self):
        pass

    def endDocument(self):
        pass
