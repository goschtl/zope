"""Base class for extractors using external files and commands.

"""
__docformat__ = "reStructuredText"

import os
import shutil
import sys
import tempfile

import zope.file.interfaces
import zope.index.text.interfaces
import zope.interface


def haveProgram(name):
    """Return true iff the program `name` is available."""
    if sys.platform.lower().startswith("win"):
        extensions = (".com", ".exe", ".bat")
    else:
        extensions = ("",)
    execpath = os.environ.get("PATH", "").split(os.path.pathsep)
    for path in execpath:
        for ext in extensions:
            fn = os.path.join(path, name + ext)
            if os.path.isfile(fn):
                return True
    return False


class WorkingDirectoryBase(object):

    zope.interface.implements(
        zope.index.text.interfaces.ISearchableText)

    # We can't use zope.component.adapts() here since the MIME-based
    # types have not been initialized; that information will need to
    # be provided via ZCML.

    def __init__(self, context):
        self.context = context
        # This could support "classic" files if an adapter is available:
        self._file = zope.file.interfaces.IFile(self.context)
        self._data = None

    def getSearchableText(self):
        if self._data is None:
            f = self._file.open("rb")
            d = tempfile.mkdtemp()
            fn = os.path.join(d, "temp" + self.extension)
            try:
                fw = open(fn, "wb")
                shutil.copyfileobj(f, fw)
                f.close()
                fw.close()
                data = self.extract(d, fn)
            finally:
                shutil.rmtree(d)
            self._data = [data]
        return self._data
        
