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

"""Code for the toFS.snarf view and its inverse, fromFS.snarf.

$Id: fssync.py,v 1.12 2003/05/20 19:09:54 gvanrossum Exp $
"""

import os
import shutil
import tempfile

from transaction import get_transaction

from zope.fssync.compare import checkUptodate

from zope.publisher.browser import BrowserView
from zope.app.fssync.syncer import toFS, fromFS
from zope.app.traversing import objectName, getParent, getRoot
from zope.app.interfaces.exceptions import UserError
from zope.fssync.snarf import Snarfer, Unsnarfer

class SnarfFile(BrowserView):

    """View returning a snarfed representation of an object tree.

    This applies to any object (for="zope.interface.Interface").
    """

    def show(self):
        """Return the snarfed response."""
        response = self.request.response
        response.setStatus(200)
        response.setHeader("Content-Type", "application/x-snarf")
        dirname = tempfile.mktemp()
        try:
            os.mkdir(dirname)
            toFS(self.context, objectName(self.context) or "root", dirname)
            snf = Snarfer(response)
            snf.addtree(dirname)
        finally:
            if os.path.isdir(dirname):
                shutil.rmtree(dirname)
        return ""

# And here is the inverse operation, fromFS.snarf.

class SnarfCommit(SnarfFile):

    """View for committing changes."""

    def commit(self):
        if not self.request.getHeader("Content-Type") == "application/x-snarf":
            self.request.response.setHeader("Content-Type", "text/plain")
            return "ERROR: Content-Type is not application/x-snarf\n"
        istr = self.request.bodyFile
        istr.seek(0)
        errors = self.do_commit(istr)
        if not errors:
            return self.show() # Return the snarfed tree!
        else:
            self.request.response.setHeader("Content-Type", "text/plain")
            errors.insert(0, "Up-to-date check failed:")
            errors.append("")
            return "\n".join(errors)

    def do_commit(self, istr):
        # 000) Set transaction note
        note = self.request.get("note")
        if not note:
            # XXX Hack because cgi doesn't parse the query string
            qs = self.request._environ.get("QUERY_STRING")
            if qs and qs.startswith("note="):
                note = qs[5:]
                import urllib
                note = urllib.unquote(note)
        if note:
            get_transaction().note(note)
        # 0) Allocate temporary names
        topdir = tempfile.mktemp()
        working = os.path.join(topdir, "working")
        current = os.path.join(topdir, "current")
        try:
            # 1) Create the top directory
            os.mkdir(topdir)
            # 2) Unsnarf into a working directory
            os.mkdir(working)
            uns = Unsnarfer(istr)
            uns.unsnarf(working)
            # 3) Save the current state of the object to disk
            os.mkdir(current)
            toFS(self.context, objectName(self.context) or "root", current)
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
            if container is None and name == "":
                # Hack to get loading the root to work; see top of fromFS().
                container = getRoot(self.context)
            fromFS(container, name, working)
            # 6) Return success
            return []
        finally:
            try:
                shutil.rmtree(topdir)
            except os.error:
                pass
