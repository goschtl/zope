"""Searchable text support for Microsoft Word documents.

This shells out to wvText, part of the wvWare package:

  http://wvware.sourceforge.net/

"""
__docformat__ = "reStructuredText"

import os
import sys

import zc.index.base


if not zc.index.base.haveProgram("wvWare"):
    del sys.modules[__name__]
    raise ImportError("external program 'wvware' is required")


class MSWordSearchableText(zc.index.base.WorkingDirectoryBase):

    extension = ".doc"

    def extract(self, directory, filename):
        cin, cout, cerr = os.popen3(
            "wvWare -d %s -x wvText.xml %s" % (directory, filename))
        data = cout.read()
        cin.close()
        cout.close()
        cerr.close()
        return unicode(data, "utf-8")
