##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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

"""Code for the toFS.zip view and its inverse, fromFS.form.

$Id: fssync.py,v 1.7 2003/05/09 20:55:37 gvanrossum Exp $
"""

import os
import shutil
import tempfile

from zope.fssync.compare import checkUptodate

from zope.publisher.browser import BrowserView
from zope.app.fssync.syncer import toFS, fromFS
from zope.app.traversing import objectName, getParent
from zope.app.interfaces.exceptions import UserError

class ZipFile(BrowserView):

    """View returning a zipped filesystem representation of an object tree.

    This applies to any object (for="zope.interface.Interface").

    Steps in the operation:
    - use toFS() to render the object tree to a temporary directory
    - cd into the directory and zip it up using the command line zip program
    - return the contents of the zipfile with content-type application/zip
    """

    def show(self, writeOriginals=None):
        """Return the zipfile response."""
        if writeOriginals is None:
            writeOriginals = isset(self.request.get("writeOriginals"))
        zipfilename = writeZipFile(self.context, writeOriginals)
        f = open(zipfilename, "rb")
        data = f.read()
        f.close()
        os.remove(zipfilename)
        response = self.request.response
        response.setHeader("Content-Type", "application/zip")
        # XXX This can return a lot of data; should figure out how to
        # do chunked writes
        response.setHeader("Content-Length", len(data))
        return data

def isset(s):
    """Helper to decide whether a string meant True or False."""
    if not s:
        return False
    s = s.strip()
    if not s:
        return False
    s = s.lower()
    istrue = isfalse = False
    for match in "true", "yes", "on", "1":
        if match.startswith(s):
            istrue = True
            break
    for match in "false", "no", "off", "0":
        if match.startswith(s):
            isfalse = True
            break
    if istrue and not isfalse:
        return True
    if isfalse and not istrue:
        return False
    raise ValueError, "invalid flag (%r)" % s

def writeZipFile(obj, writeOriginals=False):
    """Helper to render the object tree to the filesystem and zip it.

    Return the name of the zipfile.
    """
    dirname = tempfile.mktemp()
    os.mkdir(dirname)
    try:
        # XXX toFS prints to stdout; it shouldn't
        toFS(obj, objectName(obj) or "root", dirname,
             writeOriginals=writeOriginals)
        zipfilename = tempfile.mktemp(".zip")
        # XXX This is Unix specific and requires that you have the zip
        # program installed; should use the zipfile module instead
        cmd = "(cd %s; zip -q -r %s .) 2>&1" % (dirname, zipfilename)
        pipe = os.popen(cmd, "r")
        output = pipe.read()
        sts = pipe.close()
        if not sts:
            return zipfilename
        try:
            os.remove(zipfilename)
        except os.error:
            pass
        raise RuntimeError("zip status %#x; output:\n%s" % (sts, output))
    finally:
        shutil.rmtree(dirname)

# And here is the inverse operation, fromFS.html (an HTML form).

class Commit(ZipFile):

    """View for committing changes.

    For now, this is an HTML form where you can upload a zipfile.
    """

    def update(self):
        zipfile = self.request.get("zipfile")
        if zipfile is None:
            return # Not updating -- must be presenting a blank form
        else:
            zipdata = zipfile.read()
            errors = self.do_commit(zipdata)
            if not errors:
                return "Changes committed successfully."
            else:
                errors.insert(0, "Up-to-date check failed:")
                raise UserError(*errors)

    def commit(self):
        if not self.request.getHeader("Content-Type") == "application/zip":
            self.request.response.setHeader("Content-Type", "text/plain")
            return "ERROR: Content-Type is not application/zip\n"
        zipdata = self.request.body
        errors = self.do_commit(zipdata)
        if not errors:
            return self.show(writeOriginals=True) # Return the zipfile!
        else:
            self.request.response.setHeader("Content-Type", "text/plain")
            errors.insert(0, "Up-to-date check failed:")
            errors.append("")
            return "\n".join(errors)

    def do_commit(self, zipdata):
        # 00) Allocate temporary names
        topdir = tempfile.mktemp()
        zipfilename = os.path.join(topdir, "working.zip")
        working = os.path.join(topdir, "working")
        current = os.path.join(topdir, "current")
        try:
            # 0) Create the top directory
            os.mkdir(topdir)
            # 1) Write the zipfile data to disk
            f = open(zipfilename, "wb")
            f.write(zipdata)
            f.close()
            # 2) Unzip it into a working directory
            os.mkdir(working)
            os.system("cd %s; unzip -q %s" % (working, zipfilename))
            # 3) Save the current state of the object to disk
            os.mkdir(current)
            toFS(self.context, objectName(self.context) or "root", current,
                 writeOriginals=False)
            # 4) Check that the working originals are up-to-date
            errors = checkUptodate(working, current)
            if errors:
                # Make the messages nicer by editing out topdir
                errors = [x.replace(os.path.join(topdir, ""), "")
                          for x in errors]
                return errors
            # 5) Now call fromFS()
            name = objectName(self.context)
            container = getParent(self.context)
            fromFS(container, name, working)
            # 6) Return success
            return []
        finally:
            try:
                shutil.rmtree(topdir)
            except os.error:
                pass
