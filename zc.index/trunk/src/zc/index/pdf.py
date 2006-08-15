"""Searchable text support for Portable Document Format (PDF) files.

This uses the pdftotext command from xpdf to perform the extraction.

"""
__docformat__ = "reStructuredText"

import os
import sys

import zc.index.base


if not zc.index.base.haveProgram("pdftotext"):
    del sys.modules[__name__]
    raise ImportError("external program 'pdftotext' is required")


class PDFSearchableText(zc.index.base.WorkingDirectoryBase):

    extension = ".pdf"

    def extract(self, directory, filename):
        txtfile = os.path.join(directory, "words.txt")
        st = os.system("pdftotext -enc UTF-8 %s %s" % (filename, txtfile))
        f = open(txtfile, "rb")
        data = f.read()
        f.close()
        return unicode(data, "utf-8")
