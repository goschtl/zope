##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
# All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
# 
##############################################################################

"""Code for the toFS.zip view.

$Id: fssync.py,v 1.1 2003/05/08 01:08:42 gvanrossum Exp $
"""

import os
import shutil
import tempfile

from zope.publisher.browser import BrowserView
from zope.app.fssync.syncer import toFS
from zope.app.traversing import objectName

class ZipFile(BrowserView):

    """View returning a zipped filesystem representation of an object tree.

    This applies to any object (for="zope.interface.Interface").

    Steps in the operation:
    - use toFS() to render the object tree to a temporary directory
    - cd into the directory and zip it up using the command line zip program
    - return the contents of the zipfile with content-type application/zip
    """

    def show(self):
        """Return the zipfile response."""
        zipfilename = writeZipFile(self.context,
                                   self.request.get("pruneOriginals"))
        f = open(zipfilename, "rb")
        data = f.read()
        f.close()
        os.unlink(zipfilename)
        response = self.request.response
        response.setHeader("Content-Type", "application/zip")
        # XXX This can return a lot of data; should figure out how to
        # do chunked writes
        response.setHeader("Content-Length", len(data))
        return data

def writeZipFile(obj, pruneOriginals=None):
    """Helper to render the object tree to the filesystem and zip it.

    Return the name of the zipfile.
    """
    dirname = tempfile.mktemp()
    os.mkdir(dirname)
    # XXX toFS prints to stdout; it shouldn't
    toFS(obj, objectName(obj) or "root", dirname)
    if pruneOriginals:
        os.path.walk(dirname, pruneOriginalsCallback, None)
    zipfilename = tempfile.mktemp(".zip")
    # XXX This is Unix specific and requires that you have the zip
    # program installed; should use the zipfile module instead
    cmd = "(cd %s; zip -q -r %s .) 2>&1" % (dirname, zipfilename)
    pipe = os.popen(cmd, "r")
    output = pipe.read()
    sts = pipe.close()
    if sts:
        raise RuntimeError("zip status %#x; output:\n%s" % (sts, output))
    shutil.rmtree(dirname)
    return zipfilename

normcase = os.path.normcase
ZOPEDIR = normcase("@@Zope")
ORIGINAL = normcase("Original")

def pruneOriginalsCallback(arg, dirname, fnames):
    """Callback for os.path.walk() to remove 'Originals' directories."""
    # XXX toFS should be changed to omit the 'Original' directories,
    # then this function  wouldn't be needed
    base = normcase(os.path.basename(dirname))
    if base == ZOPEDIR:
        originals = filter(lambda n: normcase(n) == ORIGINAL, fnames)
        if originals:
            filter(fnames.remove, originals)
            fullname = os.path.join(dirname, ORIGINAL)
            shutil.rmtree(fullname)

# XXX Still to do: the reverse operation, fromFS.  This should
# probably be an HTML form with the zipfile as an uploaded file
